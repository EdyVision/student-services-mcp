import pytest
from unittest.mock import AsyncMock, patch
from src.client import StudentServicesMCPClient


class TestMCPClient:
    @pytest.fixture
    def client(self):
        client = StudentServicesMCPClient()
        client.session = AsyncMock()
        # Add Authorization header to the session
        client.session.headers = {"Authorization": "Bearer test123"}
        return client

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        client = StudentServicesMCPClient()
        assert client.base_url == "http://localhost:7860/mcp"
        assert client.session is None

        custom_url = "http://custom-url:8000/mcp"
        client = StudentServicesMCPClient(base_url=custom_url)
        assert client.base_url == custom_url

    @pytest.mark.asyncio
    async def test_headers_are_set(self, client):
        """Test that the Authorization header is properly set"""
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"].startswith("Bearer ")

    @pytest.mark.asyncio
    async def test_fetch_students(self, client):
        mock_response = {"status": "success", "data": ["student1", "student2"]}
        client.session.call_tool.return_value.content = mock_response

        response = await client.fetch_students()

        client.session.call_tool.assert_called_once_with(
            "fetch_students", {"limit": 100}
        )
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_check_financial_aid_eligibility(self, client):
        student_id = "test-id"
        mock_response = {"status": "success", "data": {"eligible": True}}
        client.session.call_tool.return_value.content = mock_response

        response = await client.check_financial_aid_eligibility(student_id)

        client.session.call_tool.assert_called_once_with(
            "check_financial_aid_eligibility", {"student_id": student_id}
        )
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_fetch_student_profile(self, client):
        student_id = "test-id"
        mock_response = {"status": "success", "data": {"student_info": "test"}}
        client.session.call_tool.return_value.content = mock_response

        response = await client.fetch_student_profile(student_id)

        client.session.call_tool.assert_called_once_with(
            "fetch_student_profile", {"student_id": student_id}
        )
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_fetch_academic_history(self, client):
        student_id = "test-id"
        mock_response = {"status": "success", "data": {"history": "test"}}
        client.session.call_tool.return_value.content = mock_response

        response = await client.fetch_academic_history(student_id)

        client.session.call_tool.assert_called_once_with(
            "fetch_academic_history", {"student_id": student_id}
        )
        assert response == mock_response
