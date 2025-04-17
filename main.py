# pylint: disable=unused-variable, line-too-long
import asyncio
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List
import yaml
from fastapi.openapi.docs import get_redoc_html
import uvicorn
from mcp.server import FastMCP
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

from src.adapters.clients.financial_aid import FinancialAidSystem
from src.adapters.clients.registrar import RegistrarSystem
from src.adapters.resolvers.financial_aid_resolvers import FinancialAidResolver
from src.adapters.resolvers.registrar_resolvers import RegistrarResolver


@dataclass
class AppContext:
    """Application context with our three systems."""

    financial_aid: FinancialAidResolver
    registrar: RegistrarResolver


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with our systems."""
    # Initialize systems on startup
    synthetic_data_path = "../../../dist/data/synthetic_population_data.CSV"
    synthetic_financial_aid_data_path = (
        "../../../dist/data/synthetic_financial_aid_determinations.csv"
    )
    financial_aid_system = FinancialAidSystem(synthetic_financial_aid_data_path)
    registrar_system = RegistrarSystem(synthetic_data_path)
    financial_aid_resolver = FinancialAidResolver(
        registrar=registrar_system, financial_aid=financial_aid_system
    )
    registrar_resolver = RegistrarResolver(registrar=registrar_system)

    try:
        yield AppContext(
            financial_aid=financial_aid_resolver, registrar=registrar_resolver
        )
    finally:
        # Cleanup on shutdown
        pass


# Create our MCP server with a descriptive name
mcp = FastMCP(
    "finaid-mcp",
    lifespan=app_lifespan,
    host=os.getenv("HOST", "0.0.0.0"),
    port=os.getenv("PORT", "7860"),
)

api_app = FastAPI(title="finaid-mcp")


# ===== REGISTRAR =====
@mcp.resource("students://{student_id}/profile")
async def get_student_profile(student_id: str) -> str:
    """Get a student's profile information."""
    return await mcp.get_context().request_context.lifespan_context.registrar.resolve_student_profile(
        student_id
    )


@mcp.tool()
async def fetch_student_profile(student_id: str) -> str:
    """Get a student's profile information."""
    return await mcp.get_context().request_context.lifespan_context.registrar.resolve_student_profile(
        student_id
    )


@mcp.resource("students://profiles")
async def get_students() -> List[str]:
    """Get a list of students."""
    return await mcp.get_context().request_context.lifespan_context.registrar.resolve_student_profiles(
        100
    )


@mcp.tool()
async def fetch_students(limit: int = 100) -> List[str]:
    """Get a list of students."""
    return await mcp.get_context().request_context.lifespan_context.registrar.resolve_student_profiles(
        limit
    )


@mcp.resource("students://{student_id}/academic-history")
async def get_academic_history(student_id: str) -> str:
    """Get a student's academic history."""
    return await mcp.get_context().request_context.lifespan_context.registrar.resolve_academic_history(
        student_id
    )


@mcp.tool()
async def fetch_academic_history(student_id: str) -> str:
    """Get a student's academic history."""
    return await mcp.get_context().request_context.lifespan_context.registrar.resolve_academic_history(
        student_id
    )


# ===== FINANCIAL AID =====
@mcp.resource("students://{student_id}/financial-aid")
async def get_financial_aid_eligibility(student_id: str) -> str:
    """Get programs a student is eligible for."""
    return await mcp.get_context().request_context.lifespan_context.financial_aid.resolve_financial_aid_eligibility(
        student_id
    )


@mcp.tool()
async def check_financial_aid_eligibility(student_id: str) -> str:
    """Get a student's financial aid eligibility."""
    return await mcp.get_context().request_context.lifespan_context.financial_aid.resolve_financial_aid_eligibility(
        student_id
    )


class FinancialAidMCPLogger:  # TODO: Move this to its own file
    @staticmethod
    def get_log_config():
        log_config = uvicorn.config.LOGGING_CONFIG.copy()
        log_config["formatters"]["access"][
            "fmt"
        ] = "[%(asctime)s] - %(levelname)s: %(message)s"
        log_config["formatters"]["default"][
            "fmt"
        ] = "[%(asctime)s] - %(levelname)s: %(message)s"
        return log_config

    @staticmethod
    def get_logger():
        return logging.getLogger("uvicorn.default")


# ==== SERVER ====
@api_app.get("/openapi.json", include_in_schema=False)
async def get_open_api_json():
    return JSONResponse(api_app.openapi())


@api_app.get("/openapi.yml", include_in_schema=False)
async def get_open_api_yaml():
    openapi_schema = api_app.openapi()
    yaml_schema = yaml.dump(openapi_schema)
    return Response(content=yaml_schema, media_type="text/yaml")


@api_app.get("/rest/docs", include_in_schema=False)
async def redoc_html():  # pylint: disable=unused-variable
    return get_redoc_html(
        openapi_url="/openapi.yml",
        redoc_favicon_url="/favicon.ico",
        title="Chat AI API",
    )


@api_app.get("/health")
async def mcp_root():
    """Root endpoint."""
    return JSONResponse(
        {
            "name": "Financial Aid Integration MCP",
            "version": "1.0",
            "description": "MCP server for financial aid",
            "discovery_endpoint": "/finaid-admin/mcp",
        }
    )


@mcp.resource("root://")
async def root() -> str:
    """Root endpoint for Hugging Face Spaces."""
    return "Financial Aid MCP Server is running"


@mcp.resource("health://")
async def health_check() -> str:
    """Health check endpoint."""
    return "ok"


@mcp.resource("greetings://{name}")
def get_greeting(name: str) -> str:
    """Generate a personalized greeting for the given name."""
    return f"Hello, {name}! Welcome to MCP."


async def main():
    transport = os.getenv("TRANSPORT", "sse")
    if transport == "sse":
        # Run the MCP server with sse transport
        await mcp.run_sse_async()
    else:
        # Run the MCP server with stdio transport
        await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
