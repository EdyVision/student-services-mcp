from aws_cdk import (
    Stack,
    Duration,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_elasticloadbalancingv2 as elbv2,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_logs as logs,
    aws_ssm as ssm,
    aws_ec2 as ec2,
    aws_iam as iam,
    Tags,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as certM,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_wafv2 as wafv2,
)
from constructs import Construct
import os
import json
import boto3
import urllib.request

# ==== TAGS and CONSTANTS =====
STAGE = os.getenv("STAGE")
if STAGE:
    STAGE = STAGE.lower()
DESCRIPTION = "Student Services MCP"
IMAGE = "student-services-mcp"
NAME = f"{IMAGE}-{STAGE}".lower()
TAGS = {
    "Name": NAME,
    "Repo": "https://github.com/EdyVision/student-services-mcp",
    "Service": "student-services-mcp",
    "Environment": STAGE,
}

SSM = boto3.client("ssm")

VPC_ID = "vpc-someID"
VPC_SG_ID = "sg-someID"

class StudentServicesMCPStack(Stack):
    # Use this to deploy to AWS instead - You'll need to define the VPC and Security Groups in the context
    # as well as Route53 Hosted Zone ID and Certificate ARN
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Import existing VPC by ID or name from context
        vpc = ec2.Vpc.from_lookup(self, f"{NAME}-cpv", vpc_id=VPC_ID)


        alb_sg = ec2.SecurityGroup(
            self, f"{NAME}-alb-sg", vpc=vpc, description="MCP Security Group"
        )
        alb_sg.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(443),
            description="Allow HTTPS from within VPC",
        )

        security_group = ec2.SecurityGroup.from_security_group_id(
            self, f"{NAME}-lambda-sg", [VPC_SG_ID]
        )
        zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            "HostedZone",
            hosted_zone_id="route53-hz-id",
            zone_name="route53-hz-name",
        )

        certificate_arn = SSM.get_parameter(
            Name="route53-hz-certificate-arn"
        )["Parameter"]["Value"]

        certificate = certM.Certificate.from_certificate_arn(
            self,
            f"{NAME}-certificate",
            certificate_arn=certificate_arn,
        )

        mcp_task_role = iam.Role(
            self,
            f"{NAME}-mcp-task-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        # ===== ECS Cluster and Fargate Task =====

        cluster = ecs.Cluster(self, f"{NAME.replace(' ', '')}-ecs-cluster", vpc=vpc)

        # Define Fargate Task Definition (CPU/memory can be adjusted as needed)
        task_def = ecs.FargateTaskDefinition(
            self,
            f"{NAME.replace(' ', '')}-task-def",
            cpu=512,
            memory_limit_mib=1024,
            task_role=mcp_task_role,
        )

        # Container image from ECR repository
        container_image = ecs.ContainerImage.from_asset(
            "./"
        )  # Point to the Dockerfile
        container_env = self.node.try_get_context("containerEnv")
        if not container_env:
            container_env = {
                "ENV_TYPE": STAGE,
                "LOG_LEVEL": "info",
            }

        container = task_def.add_container(
            f"{NAME.replace(' ', '')}-container",
            image=container_image,
            logging=ecs.LogDriver.aws_logs(
                stream_prefix=f"{NAME.replace(' ', '')}",
                log_group=logs.LogGroup(
                    self,
                    f"{NAME.replace(' ', '')}-log-group",
                    retention=logs.RetentionDays.ONE_WEEK,
                ),
            ),
            environment=container_env,
        )

        # If the container listens on a specific port, add port mapping (443 for HTTPS)
        # This port matches the 7860 in the Dockerfile (HuggingFace Port)
        container_port = int(self.node.try_get_context("7860") or 7860)
        container.add_port_mappings(ecs.PortMapping(container_port=container_port))

        # Create the Fargate Service to run the task
        service = ecs.FargateService(
            self,
            f"{NAME.replace(' ', '')}-fargate",
            cluster=cluster,
            task_definition=task_def,
            desired_count=int(self.node.try_get_context("desiredCount") or 2),
            assign_public_ip=False,
            min_healthy_percent=100,
            health_check_grace_period=Duration.seconds(60),
            circuit_breaker=ecs.DeploymentCircuitBreaker(enable=True, rollback=True),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[security_group],
        )

        #  Set up an Application Load Balancer for the service
        # Create a new ALB (Internet-facing by default; set to internal for now)
        lb = elbv2.ApplicationLoadBalancer(
            self,
            f"{NAME.replace(' ', '')}-alb",
            vpc=vpc,
            internet_facing=False,
            idle_timeout=Duration.seconds(1800),  # 30 minutes
            security_group=alb_sg,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        )
        lb.connections.allow_from(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(443),
            description="Allow HTTPS from within VPC"
        )

        # Create separate target groups for each listener
        root_target_group = elbv2.ApplicationTargetGroup(
            self,
            f"{NAME.replace(' ', '')}-root-target-group",
            vpc=vpc,
            port=container_port,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            health_check=elbv2.HealthCheck(
                path="/health",
                protocol=elbv2.Protocol.HTTP,
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                healthy_http_codes="200",
            ),
        )

        mcp_target_group = elbv2.ApplicationTargetGroup(
            self,
            f"{NAME.replace(' ', '')}-mcp-target-group",
            vpc=vpc,
            port=container_port,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            health_check=elbv2.HealthCheck(
                path="/health",
                protocol=elbv2.Protocol.HTTP,
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                healthy_http_codes="200",
            ),
            stickiness_cookie_duration=Duration.minutes(30),
        )

        # Add targets to the target groups
        root_target_group.add_target(service)
        mcp_target_group.add_target(service)

        # Create the HTTPS listener with the target groups
        listener = lb.add_listener(
            f"{NAME.replace(' ', '')}-https-listener",
            port=443,
            open=False,
            certificates=[certificate],
        )

        # Add the root target group as the default target
        listener.add_target_groups(
            "root-targets",
            target_groups=[root_target_group],
        )

        # Add the MCP target group with path-based routing
        listener.add_target_groups(
            "core-mcp-targets",
            target_groups=[mcp_target_group],
            priority=5,
            conditions=[
                elbv2.ListenerCondition.path_patterns(["/mcp/*", "/mcp", "/mcp*"])
            ],
        )

        # Route53 Alias to ALB
        route53.ARecord(
            self,
            f"{NAME.replace(' ', '')}-alias-record",
            zone=zone,
            record_name="student-services-mcp",  # will create student-services-mcp.*.com
            target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(lb)),
        )

        # Output the alias record for convenience
        full_domain_name = (
            "student-services-mcp.route53-hz-name"
        )

        ssm.StringParameter(
            self,
            f"{NAME.replace(' ', '')}-alias-record-param",
            parameter_name=f"/student-services-mcp/{STAGE}/alias-record",
            string_value=full_domain_name,
        )

        # Auto-scaling configuration for the ECS service
        # if bool(self.node.try_get_context("enableAutoScaling")):
        #     min_cap = int(self.node.try_get_context("minCapacity") or 2)
        #     max_cap = int(self.node.try_get_context("maxCapacity") or 5)
        #     scaling = service.auto_scale_task_count(
        #         min_capacity=min_cap, max_capacity=max_cap
        #     )
        #     scaling.scale_on_cpu_utilization(
        #         f"{NAME.replace(' ', '')}-cpu-scaling",
        #         target_utilization_percent=int(
        #             self.node.try_get_context("targetCpuUtil") or 70
        #         ),
        #         scale_in_cooldown=Duration.seconds(60),
        #         scale_out_cooldown=Duration.seconds(60),
        #     )

        # Add WAF rules to the ALB for additional protection
        waf_acl = wafv2.CfnWebACL(
            self,
            f"{NAME}-waf",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(
                block=wafv2.CfnWebACL.BlockActionProperty()
            ),
            scope="REGIONAL",
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="WAFMetric",
                sampled_requests_enabled=True,
            ),
            rules=[
                # Rule for Claude/Anthropic
                wafv2.CfnWebACL.RuleProperty(
                    name="ClaudeRule",
                    priority=1,
                    action=wafv2.CfnWebACL.RuleActionProperty(
                        allow=wafv2.CfnWebACL.AllowActionProperty()
                    ),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        or_statement=wafv2.CfnWebACL.OrStatementProperty(
                            statements=[
                                # Check Origin header
                                wafv2.CfnWebACL.StatementProperty(
                                    byte_match_statement=wafv2.CfnWebACL.ByteMatchStatementProperty(
                                        field_to_match=wafv2.CfnWebACL.FieldToMatchProperty(
                                            single_header=wafv2.CfnWebACL.SingleHeaderProperty(
                                                name="Origin"
                                            )
                                        ),
                                        positional_constraint="CONTAINS",
                                        search_string="anthropic.com",
                                        text_transformations=[
                                            wafv2.CfnWebACL.TextTransformationProperty(
                                                priority=1, type="NONE"
                                            )
                                        ],
                                    )
                                ),
                                # Check User-Agent header
                                wafv2.CfnWebACL.StatementProperty(
                                    byte_match_statement=wafv2.CfnWebACL.ByteMatchStatementProperty(
                                        field_to_match=wafv2.CfnWebACL.FieldToMatchProperty(
                                            single_header=wafv2.CfnWebACL.SingleHeaderProperty(
                                                name="User-Agent"
                                            )
                                        ),
                                        positional_constraint="CONTAINS",
                                        search_string="anthropic",
                                        text_transformations=[
                                            wafv2.CfnWebACL.TextTransformationProperty(
                                                priority=1, type="NONE"
                                            )
                                        ],
                                    )
                                )
                            ]
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name="ClaudeRuleMetric",
                        sampled_requests_enabled=True,
                    ),
                ),
            ],
        )

        # Associate WAF with ALB
        wafv2.CfnWebACLAssociation(
            self,
            "WAFAssociation",
            resource_arn=lb.load_balancer_arn,
            web_acl_arn=waf_acl.attr_arn,
        )

        self._add_tags()

    def _add_tags(self):
        """add tags to all resources in stack"""

        for key, value in TAGS.items():
            Tags.of(self).add(key, value)

    def _get_cloudfront_ips(self):
        """Get the list of CloudFront IP ranges from AWS."""
        url = "https://ip-ranges.amazonaws.com/ip-ranges.json"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        cloudfront_ips = []
        for prefix in data["prefixes"]:
            if prefix["service"] == "CLOUDFRONT":
                cloudfront_ips.append(prefix["ip_prefix"])
        return cloudfront_ips
