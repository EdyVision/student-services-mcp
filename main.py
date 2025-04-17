import uvicorn
from fastapi import FastAPI, Request
from fastapi_mcp import FastApiMCP

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List
from starlette.responses import JSONResponse

from src.adapters.clients.financial_aid import FinancialAidSystem
from src.adapters.clients.registrar import RegistrarSystem
from src.adapters.resolvers.financial_aid_resolvers import FinancialAidResolver
from src.adapters.resolvers.registrar_resolvers import RegistrarResolver
from src.config.settings import settings

# ==== CONTEXT ====


@dataclass
class AppContext:
    """Application context with our three systems."""

    financial_aid: FinancialAidResolver
    registrar: RegistrarResolver


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with our systems."""
    # Initialize systems on startup
    synthetic_data_path = "../../../dist/data/synthetic_population_data.csv"

    financial_aid_system = FinancialAidSystem()
    registrar_system = RegistrarSystem(synthetic_data_path)
    financial_aid_resolver = FinancialAidResolver(
        registrar=registrar_system, financial_aid=financial_aid_system
    )
    registrar_resolver = RegistrarResolver(registrar=registrar_system)

    app.state.financial_aid_resolver = financial_aid_resolver
    app.state.registrar_resolver = registrar_resolver

    try:

        yield
    finally:
        # Cleanup on shutdown
        pass


# Existing FastAPI application
app = FastAPI(lifespan=app_lifespan)

mcp = FastApiMCP(
    app,
    name=settings.common.APP_NAME,
    description=settings.common.APP_DESCRIPTION,
    base_url=f"http://{settings.server.HOST}:{settings.server.PORT}",
)

# ==== MOUNT MCP ====
mcp.mount()


# ==== ENDPOINTS ====
@app.get("/")
async def root():
    return JSONResponse(
        {
            "name": settings.common.APP_NAME,
            "version": settings.common.APP_VERSION,
            "description": settings.common.APP_DESCRIPTION,
            "discovery_endpoint": "/mcp",
        }
    )


@app.get("/students/{student_id}/profile", operation_id="fetch_student_profile")
async def fetch_student_profile(student_id: str, request: Request):
    """Get a student's profile information."""
    return await request.app.state.registrar_resolver.resolve_student_profile(
        student_id
    )


@app.get("/students", operation_id="fetch_students")
async def fetch_students(limit: int, request: Request):
    """Get a list of students."""
    return await request.app.state.registrar_resolver.resolve_student_profiles(limit)


@app.get(
    "/students/{student_id}/academic-history", operation_id="fetch_academic_history"
)
async def fetch_academic_history(student_id: str, request: Request):
    """Get a student's academic history."""
    return await request.app.state.registrar_resolver.resolve_academic_history(
        student_id
    )


@app.get(
    "/students/{student_id}/financial-aid",
    operation_id="check_financial_aid_eligibility",
)
async def check_financial_aid_eligibility(student_id: str, request: Request):
    """Get a student's financial aid eligibility."""
    return await request.app.state.financial_aid_resolver.resolve_financial_aid_eligibility(
        student_id
    )


# ==== RUN THE APP ====
mcp.setup_server()

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host=settings.server.HOST, port=settings.server.PORT)
