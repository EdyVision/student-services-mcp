import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi_mcp import FastApiMCP, AuthConfig

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from starlette.responses import JSONResponse

from src.adapters.clients.financial_aid import FinancialAidSystem
from src.adapters.clients.registrar import RegistrarSystem
from src.adapters.resolvers.financial_aid_resolvers import FinancialAidResolver
from src.adapters.resolvers.registrar_resolvers import RegistrarResolver
from src.config.settings import settings
from src.middleware.auth import verify_auth


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

# Configure MCP with conditional authentication
if settings.auth.AUTH_ENABLED:
    mcp = FastApiMCP(
        app,
        name=settings.common.APP_NAME,
        description=settings.common.APP_DESCRIPTION,
        auth_config=AuthConfig(
            dependencies=[Depends(verify_auth)],
        ),
    )
else:
    mcp = FastApiMCP(
        app,
        name=settings.common.APP_NAME,
        description=settings.common.APP_DESCRIPTION,
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


@app.get(
    "/students/{student_id}/profile",
    operation_id="fetch_student_profile",
    description="Get a student's profile information by student_id.",
)
async def fetch_student_profile(student_id: str, request: Request):
    """Get a student's profile information."""
    return await request.app.state.registrar_resolver.resolve_student_profile(
        student_id
    )


@app.get(
    "/students/by-name/{student_name}/profile",
    operation_id="fetch_student_profile_by_name",
    description="Get a student's profile information by student_name (case-insensitive full name).",
)
async def fetch_student_profile_by_name(student_name: str, request: Request):
    """Get a student's profile information by student_name (case-insensitive)."""
    return await request.app.state.registrar_resolver.resolve_student_profile_by_name(
        student_name
    )


@app.get(
    "/students",
    operation_id="fetch_students",
    description="Get a list of students, limited by the 'limit' query parameter.",
)
async def fetch_students(limit: int, request: Request):
    """Get a list of students."""
    return await request.app.state.registrar_resolver.resolve_student_profiles(limit)


@app.get(
    "/students/{student_id}/academic-history",
    operation_id="fetch_academic_history",
    description="Get a student's academic history (all past terms and courses) by student_id.",
)
async def fetch_academic_history(student_id: str, request: Request):
    """Get a student's academic history."""
    return await request.app.state.registrar_resolver.resolve_academic_history(
        student_id
    )


@app.get(
    "/students/{student_id}/financial-aid",
    operation_id="fetch_financial_aid_eligibility",
    description="Get a student's financial aid eligibility by student_id.",
)
async def fetch_financial_aid_eligibility(student_id: str, request: Request):
    """Get a student's financial aid eligibility."""
    return await request.app.state.financial_aid_resolver.resolve_financial_aid_eligibility(
        student_id
    )


@app.post(
    "/students/{student_id}/notes",
    operation_id="submit_note",
    description="Submit a note and stress level for a student by student_id.",
)
async def submit_note(student_id: str, note: str, stress_level: str, request: Request):
    """Submit a note and stress level for a student."""
    return await request.app.state.registrar_resolver.submit_note(
        student_id, note, stress_level
    )


@app.post(
    "/students/{student_id}/course-plan",
    operation_id="fetch_course_plan",
    description="Get a course plan for a student based on stress level and target credits.",
)
async def fetch_course_plan(
    student_id: str, target_credits: int, stress_level: str, request: Request
):
    """Get a course plan based on stress level and target credits."""
    return await request.app.state.registrar_resolver.generate_course_plan(
        student_id, target_credits, stress_level
    )


@app.post(
    "/students/{student_id}/submit-plan",
    operation_id="submit_course_plan",
    description="Submit a course plan with justification or reflection from student using the student's reflection as the justification.",
)
async def submit_course_plan(
    student_id: str, plan: str, justification: str, request: Request
):
    """Submit a course plan with justification or reflection from student."""
    return await request.app.state.registrar_resolver.submit_course_plan(
        student_id, plan, justification
    )


# ==== RUN THE APP ====
mcp.setup_server()

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host=settings.server.HOST, port=settings.server.PORT)
