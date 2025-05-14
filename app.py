#!/usr/bin/env python3
import aws_cdk as cdk
import os
from cdk.stack import StudentServicesMCPStack, NAME, TAGS, DESCRIPTION

REGION = os.getenv("CDK_DEFAULT_REGION")
ACCOUNT = os.getenv("CDK_DEFAULT_ACCOUNT")

app = cdk.App()

StudentServicesMCPStack(
    app,
    f"{NAME}",
    description=DESCRIPTION,
    tags=TAGS,
    env={"account": ACCOUNT, "region": REGION},
)

app.synth()
