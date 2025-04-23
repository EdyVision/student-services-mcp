import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse
from starlette.testclient import TestClient
from middleware.auth import AuthMiddleware
from middleware.agent_validator import AgentValidatorMiddleware
from config.settings import settings


@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.headers = {}
    return request


@pytest.fixture
def mock_app():
    app = FastAPI()
    return app


@pytest.fixture
def test_client(mock_app):
    return TestClient(mock_app)


async def mock_call_next(request):
    return JSONResponse({"message": "success"})


class TestAuthMiddleware:
    @pytest.mark.asyncio
    async def test_auth_skipped_for_root_endpoint(self, mock_request):
        mock_request.url.path = "/"
        middleware = AuthMiddleware(mock_app)
        response = await middleware.dispatch(mock_request, mock_call_next)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_auth_skipped_for_mcp_endpoint(self, mock_request):
        mock_request.url.path = "/mcp"
        middleware = AuthMiddleware(mock_app)
        response = await middleware.dispatch(mock_request, mock_call_next)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_auth_skipped_when_disabled(self, mock_request):
        with patch.object(settings.auth, "AUTH_ENABLED", False):
            middleware = AuthMiddleware(mock_app)
            response = await middleware.dispatch(mock_request, mock_call_next)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_auth_missing_header(self, mock_request):
        with patch.object(settings.auth, "AUTH_ENABLED", True):
            middleware = AuthMiddleware(mock_app)
            with pytest.raises(HTTPException) as exc_info:
                await middleware.dispatch(mock_request, mock_call_next)
            assert exc_info.value.status_code == 401
            assert "Authorization header is missing" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_auth_invalid_scheme(self, mock_request):
        with patch.object(settings.auth, "AUTH_ENABLED", True):
            mock_request.headers = {"Authorization": "Basic token"}
            middleware = AuthMiddleware(mock_app)
            with pytest.raises(HTTPException) as exc_info:
                await middleware.dispatch(mock_request, mock_call_next)
            assert exc_info.value.status_code == 401
            assert "Invalid authentication scheme" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_auth_invalid_token(self, mock_request):
        with patch.object(settings.auth, "AUTH_ENABLED", True):
            mock_request.headers = {"Authorization": "Bearer invalid_token"}
            with patch.object(settings.auth, "AUTH_TOKEN", "valid_token"):
                middleware = AuthMiddleware(mock_app)
                with pytest.raises(HTTPException) as exc_info:
                    await middleware.dispatch(mock_request, mock_call_next)
                assert exc_info.value.status_code == 401
                assert "Invalid token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_auth_valid_token(self, mock_request):
        with patch.object(settings.auth, "AUTH_ENABLED", True):
            mock_request.headers = {"Authorization": "Bearer valid_token"}
            with patch.object(settings.auth, "AUTH_TOKEN", "valid_token"):
                middleware = AuthMiddleware(mock_app)
                response = await middleware.dispatch(mock_request, mock_call_next)
                assert response.status_code == 200


class TestAgentValidatorMiddleware:
    @pytest.mark.asyncio
    async def test_agent_validation_skipped_for_root_endpoint(self, mock_request):
        mock_request.url.path = "/"
        middleware = AgentValidatorMiddleware(mock_app)
        response = await middleware.dispatch(mock_request, mock_call_next)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_agent_validation_skipped_for_mcp_endpoint(self, mock_request):
        mock_request.url.path = "/mcp"
        middleware = AgentValidatorMiddleware(mock_app)
        response = await middleware.dispatch(mock_request, mock_call_next)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_agent_validation_skipped_when_disabled(self, mock_request):
        with patch.object(settings.agent, "AGENT_VALIDATION_ENABLED", False):
            middleware = AgentValidatorMiddleware(mock_app)
            response = await middleware.dispatch(mock_request, mock_call_next)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_agent_validation_missing_header(self, mock_request):
        with patch.object(settings.agent, "AGENT_VALIDATION_ENABLED", True):
            middleware = AgentValidatorMiddleware(mock_app)
            with pytest.raises(HTTPException) as exc_info:
                await middleware.dispatch(mock_request, mock_call_next)
            assert exc_info.value.status_code == 403
            assert "X-Agent-Type header is required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_agent_validation_invalid_agent(self, mock_request):
        with patch.object(settings.agent, "AGENT_VALIDATION_ENABLED", True):
            mock_request.headers = {"X-Agent-Type": "chatgpt"}
            with patch.object(settings.agent, "ALLOWED_AGENTS", ["cursor", "claude", "custom"]):
                middleware = AgentValidatorMiddleware(mock_app)
                with pytest.raises(HTTPException) as exc_info:
                    await middleware.dispatch(mock_request, mock_call_next)
                assert exc_info.value.status_code == 403
                assert "Agent type 'chatgpt' is not allowed" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_agent_validation_valid_agent(self, mock_request):
        with patch.object(settings.agent, "AGENT_VALIDATION_ENABLED", True):
            mock_request.headers = {"X-Agent-Type": "cursor"}
            with patch.object(settings.agent, "ALLOWED_AGENTS", ["cursor", "claude", "custom"]):
                middleware = AgentValidatorMiddleware(mock_app)
                response = await middleware.dispatch(mock_request, mock_call_next)
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_agent_validation_case_insensitive(self, mock_request):
        with patch.object(settings.agent, "AGENT_VALIDATION_ENABLED", True):
            mock_request.headers = {"X-Agent-Type": "CURSOR"}
            with patch.object(settings.agent, "ALLOWED_AGENTS", ["cursor", "claude", "custom"]):
                middleware = AgentValidatorMiddleware(mock_app)
                response = await middleware.dispatch(mock_request, mock_call_next)
                assert response.status_code == 200 