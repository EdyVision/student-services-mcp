from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class AgentValidatorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Print and log all headers for debugging
        headers = dict(request.headers)
        print(f"\n=== Agent Validator Middleware ===")
        print(f"Path: {request.url.path}")
        print(f"Method: {request.method}")
        print("\nHeaders (case-sensitive):")
        for name, value in request.headers.raw:
            print(f"  {name.decode()}: {value.decode()}")
        print("\nParsed headers:")
        print(f"  X-Agent-Type: {headers.get('X-Agent-Type')}")
        print(f"  x-agent-type: {headers.get('x-agent-type')}")
        print("===============================\n")
        
        logger.info(f"Received headers: {headers}")

        # Skip agent validation for the root endpoint and MCP endpoint
        if request.url.path in ["/", "/mcp"]:
            print("Skipping validation for root or MCP endpoint")
            return await call_next(request)

        # Skip validation if disabled in settings
        if not settings.agent.AGENT_VALIDATION_ENABLED:
            print("Agent validation is disabled in settings")
            return await call_next(request)

        # Get the X-Agent-Type header (case-insensitive)
        agent_type = request.headers.get("X-Agent-Type") or request.headers.get("x-agent-type")
        if not agent_type:
            print("ERROR: X-Agent-Type header is missing")
            raise HTTPException(
                status_code=403,
                detail="X-Agent-Type header is required"
            )

        # Check if the agent type is allowed
        if agent_type.lower() not in [agent.lower() for agent in settings.agent.ALLOWED_AGENTS]:
            print(f"ERROR: Invalid agent type: {agent_type}")
            raise HTTPException(
                status_code=403,
                detail=f"Agent type '{agent_type}' is not allowed. Allowed agents: {', '.join(settings.agent.ALLOWED_AGENTS)}"
            )

        print(f"Agent validation passed for type: {agent_type}")
        # If everything is valid, proceed with the request
        return await call_next(request) 