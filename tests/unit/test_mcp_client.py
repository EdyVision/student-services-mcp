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
    async def test_fetch_financial_aid_eligibility(self, client):
        student_id = "test-id"
        mock_response = {"status": "success", "data": {"eligible": True}}
        client.session.call_tool.return_value.content = mock_response

        response = await client.fetch_financial_aid_eligibility(student_id)

        client.session.call_tool.assert_called_once_with(
            "fetch_financial_aid_eligibility", {"student_id": student_id}
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

    # Analytics tools tests
    @pytest.mark.asyncio
    async def test_fetch_student_dropout_risk(self, client):
        student_id = "test-id"
        mock_response = {"status": "success", "data": {"dropout_risk": True, "probability": 0.8}}
        client.session.call_tool.return_value.content = mock_response

        response = await client.fetch_student_dropout_risk(student_id)

        client.session.call_tool.assert_called_once_with(
            "fetch_student_dropout_risk", {"student_id": student_id}
        )
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_fetch_high_risk_students(self, client):
        limit = 5
        mock_response = {"status": "success", "data": [{"student_id": "S001", "risk": 0.9}]}
        client.session.call_tool.return_value.content = mock_response

        response = await client.fetch_high_risk_students(limit)

        client.session.call_tool.assert_called_once_with(
            "fetch_high_risk_students", {"limit": limit}
        )
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_fetch_high_risk_students_default_limit(self, client):
        mock_response = {"status": "success", "data": []}
        client.session.call_tool.return_value.content = mock_response

        response = await client.fetch_high_risk_students()

        client.session.call_tool.assert_called_once_with(
            "fetch_high_risk_students", {"limit": 10}
        )
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_fetch_attrition_statistics(self, client):
        mock_response = {"status": "success", "data": {"total_students": 100, "dropout_rate": 0.15}}
        client.session.call_tool.return_value.content = mock_response

        response = await client.fetch_attrition_statistics()

        client.session.call_tool.assert_called_once_with(
            "fetch_attrition_statistics", {}
        )
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_fetch_student_attrition_analysis(self, client):
        student_id = "test-id"
        mock_response = {"status": "success", "data": {"factors": ["low_gpa", "high_work_hours"]}}
        client.session.call_tool.return_value.content = mock_response

        response = await client.fetch_student_attrition_analysis(student_id)

        client.session.call_tool.assert_called_once_with(
            "fetch_student_attrition_analysis", {"student_id": student_id}
        )
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_fetch_attrition_feature_importance(self, client):
        mock_response = {"status": "success", "data": {"correlation_analysis": {"gpa": 0.8}}}
        client.session.call_tool.return_value.content = mock_response

        response = await client.fetch_attrition_feature_importance()

        client.session.call_tool.assert_called_once_with(
            "fetch_attrition_feature_importance", {}
        )
        assert response == mock_response
