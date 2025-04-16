import asyncio
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List

import uvicorn
from mcp.server import FastMCP, Server
from mcp.server.fastmcp.server import Settings
# from fastapi import FastAPI, Response
# from fastapi.middleware.cors import CORSMiddleware

from src.systems.claims import ClaimsSystem
from src.systems.eligibility import EligibilitySystem
from src.systems.records import RecordsSystem


@dataclass
class AppContext:
    """Application context with our three systems."""

    eligibility: EligibilitySystem
    claims: ClaimsSystem
    records: RecordsSystem


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with our systems."""
    # Initialize systems on startup
    eligibility_system = EligibilitySystem()
    claims_system = ClaimsSystem()
    records_system = RecordsSystem()

    try:
        yield AppContext(
            eligibility=eligibility_system, claims=claims_system, records=records_system
        )
    finally:
        # Cleanup on shutdown
        await eligibility_system.disconnect()
        await claims_system.disconnect()
        await records_system.disconnect()


# Create our MCP server with a descriptive name
mcp = FastMCP("finaid-mcp", lifespan=app_lifespan, host=os.getenv("HOST", "0.0.0.0"),
    port=os.getenv("PORT", "7860"))

# Add CORS middleware
# mcp.app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Add root endpoint for Hugging Face Spaces
@mcp.resource("root://")
async def root() -> str:
    """Root endpoint for Hugging Face Spaces."""
    return "Financial Aid MCP Server is running"

# Add health check endpoint
@mcp.resource("health://")
async def health_check() -> str:
    """Health check endpoint."""
    return "ok"

# ===== RESOURCES =====
@mcp.resource("students://{student_id}/profile")
async def get_student_profile(student_id: str) -> str:
    """Get a student's profile information."""
    try:
        records_system = mcp.get_context().request_context.lifespan_context.records
        profile = records_system.get_student_profile(student_id)

        if not profile:
            return f"Student with ID {student_id} not found."

        response = f"Student {profile['name']} (ID: {profile['student_id']}) has a GPA of {profile['gpa']} in {profile['major']}."
    except Exception as e:
        response = f"Error retrieving student profile: {str(e)}"

    return response


@mcp.resource("students://profiles")
async def get_students() -> List[str]:
    """Get a list of students."""
    records_system = mcp.get_context().request_context.lifespan_context.records
    profiles = records_system.get_student_profiles(100)
    return profiles


@mcp.resource("students://{student_id}/academic-history")
async def get_academic_history(student_id: str) -> str:
    """Get a student's academic history."""
    records = mcp.get_context().request_context.lifespan_context.records
    history = records.get_academic_history_handler(student_id)
    return history


@mcp.resource("students://{student_id}/financial-aid")
async def get_financial_aid_eligibility(student_id: str) -> str:
    """Get programs a student is eligible for."""
    records_system = mcp.get_context().request_context.lifespan_context.records
    eligibility = mcp.get_context().request_context.lifespan_context.eligibility

    # Retrieve student info
    profile = records_system.get_student_profile(student_id)

    # Then check eligibility
    requirements, financial_aid = eligibility.determine_financial_aid_eligibility(
        profile["gpa"], profile["major"]
    )

    if financial_aid:
        return f"Student {profile['name']} (ID: {student_id}) has a GPA of {profile['gpa']} in {profile['major']}. They are eligible for the {financial_aid}. Requirements: {requirements}"
    else:
        return f"Student {profile['name']} (ID: {student_id}) has a GPA of {profile['gpa']} in {profile['major']}. They are not eligible for financial aid. Requirements: {requirements if requirements else 'Requirements unspecified for program or major.'}"


@mcp.resource("greetings://{name}")
def get_greeting(name: str) -> str:
    """Generate a personalized greeting for the given name."""
    return f"Hello, {name}! Welcome to MCP."


# ==== TOOLS ====
@mcp.tool()
async def fetch_student(student_id: str) -> str:
    """Get a student's profile information."""
    # Create systems directly rather than accessing via MCP context
    records_system = mcp.get_context().request_context.lifespan_context.records
    profile = records_system.get_student_profile(student_id)

    return f"""Student {profile['name']} (ID: {profile['student_id']}) has a GPA of {profile['gpa']} in {profile['major']} and an income of ${profile['income']}."""


@mcp.tool()
async def fetch_students() -> List[str]:
    """Get a list of students."""
    records_system = mcp.get_context().request_context.lifespan_context.records
    profiles = records_system.get_student_profiles(100)
    return profiles


@mcp.tool()
async def check_eligibility(student_id: str) -> str:
    """Get a student's financial aid eligibility."""
    # Create systems directly rather than accessing via MCP context
    records_system = mcp.get_context().request_context.lifespan_context.records
    eligibility = mcp.get_context().request_context.lifespan_context.eligibility

    # Retrieve student info
    profile = records_system.get_student_profile(student_id)

    # Then check eligibility
    requirements, financial_aid = eligibility.determine_financial_aid_eligibility(
        profile["gpa"], profile["major"]
    )

    if financial_aid:
        return f"Student {profile['name']} (ID: {student_id}) has a GPA of {profile['gpa']} in {profile['major']}. They are eligible for the {financial_aid}. Requirements: {requirements}"
    else:
        return f"Student {profile['name']} (ID: {student_id}) has a GPA of {profile['gpa']} in {profile['major']}. They are not eligible for financial aid. Requirements: {requirements if requirements else 'Requirements unspecified for program or major.'}"

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



async def main():
    transport = os.getenv("TRANSPORT", "sse")
    if transport == 'sse':
        # Run the MCP server with sse transport
        await mcp.run_sse_async()
    else:
        # Run the MCP server with stdio transport
        await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
