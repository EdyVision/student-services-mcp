import pytest
from unittest.mock import AsyncMock, MagicMock
from src.adapters.resolvers.analyses_resolvers import AnalysesResolver
from src.adapters.systems.analyses import StudentAnalysesSystem


class TestAnalysesResolver:
    """Test cases for AnalysesResolver."""

    @pytest.fixture
    def mock_analyses_system(self):
        """Create a mock analyses system."""
        system = MagicMock(spec=StudentAnalysesSystem)
        return system

    @pytest.fixture
    def resolver(self, mock_analyses_system):
        """Create a resolver with mocked dependencies."""
        return AnalysesResolver(analyses=mock_analyses_system)

    @pytest.mark.asyncio
    async def test_resolve_student_dropout_risk_success(
        self, resolver, mock_analyses_system
    ):
        """Test successful dropout risk prediction."""
        # Mock the system response
        mock_result = {
            "student_id": "S12345",
            "name": "John Doe",
            "dropout_probability": 0.35,
            "dropout_risk": False,
            "risk_level": "Medium",
            "attrition_features": {
                "semesters_completed": 2,
                "credits_attempted": 30,
                "credits_completed": 30,
                "completion_rate": 1.0,
                "failed_courses": 0,
                "withdrawn_courses": 0,
                "gpa_trend": "stable",
                "attendance_rate": 0.95,
                "stress_frequency": 1,
                "course_load_variance": 0.0,
                "graduation_timeline_risk": "delayed",
            },
            "recommendations": ["Graduation timeline at risk - review academic plan"],
        }
        mock_analyses_system.predict_dropout_risk = AsyncMock(return_value=mock_result)

        # Test the resolver
        result = await resolver.resolve_student_dropout_risk("S12345")

        # Verify the system was called correctly
        mock_analyses_system.predict_dropout_risk.assert_called_once_with("S12345")

        # Verify the response format
        assert "Dropout Risk Prediction for John Doe (S12345)" in result
        assert "Risk Level: Medium" in result
        assert "Dropout Probability: 35.0%" in result
        assert "High Risk Flag: No" in result
        assert "Semesters Completed: 2" in result
        assert "Completion Rate: 100.0%" in result
        assert "1. Graduation timeline at risk - review academic plan" in result

    @pytest.mark.asyncio
    async def test_resolve_student_dropout_risk_error(
        self, resolver, mock_analyses_system
    ):
        """Test dropout risk prediction with error."""
        # Mock the system response with error
        mock_result = {"error": "Student not found"}
        mock_analyses_system.predict_dropout_risk = AsyncMock(return_value=mock_result)

        # Test the resolver
        result = await resolver.resolve_student_dropout_risk("S99999")

        # Verify the error response
        assert "Error: Student not found" in result

    @pytest.mark.asyncio
    async def test_resolve_high_risk_students_success(
        self, resolver, mock_analyses_system
    ):
        """Test successful high-risk students retrieval."""
        # Mock the system response
        mock_students = [
            {
                "student_id": "S11111",
                "name": "Alice Smith",
                "gpa": 2.1,
                "year": "Junior",
                "dropout_probability": 0.95,
                "completion_rate": 0.36,
                "failed_courses": 6,
                "attendance_rate": 0.796,
            },
            {
                "student_id": "S22222",
                "name": "Bob Johnson",
                "gpa": 2.19,
                "year": "Sophomore",
                "dropout_probability": 0.95,
                "completion_rate": 0.414,
                "failed_courses": 12,
                "attendance_rate": 0.776,
            },
        ]
        mock_analyses_system.get_high_risk_students = AsyncMock(
            return_value=mock_students
        )

        # Test the resolver
        result = await resolver.resolve_high_risk_students(limit=2)

        # Verify the system was called correctly
        mock_analyses_system.get_high_risk_students.assert_called_once_with(2)

        # Verify the response format
        assert "High-Risk Students (Top 2):" in result
        assert "1. Alice Smith (S11111)" in result
        assert "2. Bob Johnson (S22222)" in result
        assert "Dropout Probability: 95.0%" in result
        assert "Completion Rate: 36.0%" in result

    @pytest.mark.asyncio
    async def test_resolve_high_risk_students_empty(
        self, resolver, mock_analyses_system
    ):
        """Test high-risk students retrieval with no results."""
        # Mock empty response
        mock_analyses_system.get_high_risk_students = AsyncMock(return_value=[])

        # Test the resolver
        result = await resolver.resolve_high_risk_students()

        # Verify the response
        assert "No high-risk students found." in result

    @pytest.mark.asyncio
    async def test_resolve_attrition_statistics_success(
        self, resolver, mock_analyses_system
    ):
        """Test successful attrition statistics retrieval."""
        # Mock the system response
        mock_stats = {
            "total_students": 1000,
            "dropout_count": 458,
            "dropout_rate": 0.458,
            "high_risk_count": 459,
            "high_risk_rate": 0.459,
            "average_dropout_probability": 0.461,
            "dropout_by_year": {
                "Freshman": {"total": 250, "dropouts": 130, "dropout_rate": 0.52},
                "Sophomore": {"total": 250, "dropouts": 118, "dropout_rate": 0.472},
                "Junior": {"total": 250, "dropouts": 115, "dropout_rate": 0.46},
                "Senior": {"total": 250, "dropouts": 95, "dropout_rate": 0.38},
            },
        }
        mock_analyses_system.get_attrition_statistics = AsyncMock(
            return_value=mock_stats
        )

        # Test the resolver
        result = await resolver.resolve_attrition_statistics()

        # Verify the system was called correctly
        mock_analyses_system.get_attrition_statistics.assert_called_once()

        # Verify the response format
        assert "Attrition Statistics Report" in result
        assert "Total Students: 1,000" in result
        assert "Students Who Dropped Out: 458" in result
        assert "Overall Dropout Rate: 45.8%" in result
        assert "High-Risk Students: 459" in result
        assert "Freshman: 130/250 (52.0%)" in result
        assert "Senior: 95/250 (38.0%)" in result

    @pytest.mark.asyncio
    async def test_resolve_attrition_statistics_error(
        self, resolver, mock_analyses_system
    ):
        """Test attrition statistics with error."""
        # Mock error response
        mock_analyses_system.get_attrition_statistics = AsyncMock(
            return_value={"error": "No data available"}
        )

        # Test the resolver
        result = await resolver.resolve_attrition_statistics()

        # Verify the error response
        assert "Error: No data available" in result

    @pytest.mark.asyncio
    async def test_resolve_attrition_feature_importance_success(
        self, resolver, mock_analyses_system
    ):
        """Test successful attrition feature importance analysis."""
        # Mock the system response
        mock_analysis = {
            "correlation_analysis": {
                "gpa": 0.352,
                "completion_rate": 0.297,
                "attendance_rate": 0.326,
                "failed_courses": 0.272,
                "dropout_probability": 0.450,
            },
            "model_importance": {
                "gpa": 0.35,
                "completion_rate": 0.30,
                "attendance_rate": 0.25,
                "failed_courses": 0.20,
            },
            "categorical_analysis": {
                "gpa_trend_dropout_rates": {
                    "improving": 0.25,
                    "stable": 0.40,
                    "declining": 0.65,
                },
                "timeline_risk_dropout_rates": {
                    "on_track": 0.20,
                    "at_risk": 0.45,
                    "delayed": 0.60,
                },
                "year_dropout_rates": {
                    "Freshman": 0.52,
                    "Sophomore": 0.47,
                    "Junior": 0.46,
                    "Senior": 0.38,
                },
            },
            "total_students_analyzed": 1000,
            "insights": [
                "'gpa' is the strongest predictor of dropout (correlation: 0.352)",
                "Students with declining GPA trend have 65.0% dropout rate vs 40.0% for stable trend",
            ],
        }
        mock_analyses_system.get_attrition_feature_importance = AsyncMock(
            return_value=mock_analysis
        )

        # Test the resolver
        result = await resolver.resolve_attrition_feature_importance()

        # Verify the system was called correctly
        mock_analyses_system.get_attrition_feature_importance.assert_called_once()

        # Verify the response format
        assert "Feature Importance Analysis for Dropout Prediction" in result
        assert "CORRELATION ANALYSIS (Top 10 Features):" in result
        assert "1. gpa                  | Correlation: 0.352" in result
        assert "MODEL IMPORTANCE WEIGHTS:" in result
        assert "• gpa                  | Weight: 0.35" in result
        assert "GPA Trend Dropout Rates:" in result
        assert "• declining  | Dropout Rate: 65.0%" in result
        assert "KEY INSIGHTS:" in result
        assert (
            "1. 'gpa' is the strongest predictor of dropout (correlation: 0.352)"
            in result
        )
        assert "Total Students Analyzed: 1,000" in result

    @pytest.mark.asyncio
    async def test_resolve_attrition_feature_importance_error(
        self, resolver, mock_analyses_system
    ):
        """Test attrition feature importance with error."""
        # Mock error response
        mock_analyses_system.get_attrition_feature_importance = AsyncMock(
            return_value={"error": "No data available"}
        )

        # Test the resolver
        result = await resolver.resolve_attrition_feature_importance()

        # Verify the error response
        assert "Error: No data available" in result

    @pytest.mark.asyncio
    async def test_resolve_attrition_factor_analysis_success(
        self, resolver, mock_analyses_system
    ):
        """Test successful attrition factor analysis for a student."""
        # Mock the system response
        mock_result = {
            "student_id": "S12345",
            "name": "John Doe",
            "dropout_probability": 0.75,
            "dropout_risk": True,
            "risk_level": "High",
            "attrition_features": {
                "gpa": 2.1,
                "gpa_trend": "declining",
                "completion_rate": 0.65,
                "failed_courses": 4,
                "withdrawn_courses": 1,
                "attendance_rate": 0.75,
                "stress_frequency": 3,
                "course_load_variance": 45.2,
                "graduation_timeline_risk": "delayed",
            },
            "recommendations": [
                "Immediate intervention recommended - student is at very high risk",
                "Focus on improving course completion - consider academic support",
                "Multiple course failures detected - recommend tutoring or course retake",
            ],
        }
        mock_analyses_system.predict_dropout_risk = AsyncMock(return_value=mock_result)

        # Test the resolver
        result = await resolver.resolve_attrition_factor_analysis("S12345")

        # Verify the system was called correctly
        mock_analyses_system.predict_dropout_risk.assert_called_once_with("S12345")

        # Verify the response format
        assert "Attrition Factor Analysis for John Doe (S12345)" in result
        assert "ACADEMIC PERFORMANCE FACTORS:" in result
        assert "• Current GPA: 2.1" in result
        assert "• GPA Trend: declining ⚠️" in result
        assert "• Completion Rate: 65.0% ⚠️" in result
        assert "• Failed Courses: 4 ⚠️" in result
        assert "RISK ASSESSMENT:" in result
        assert "• Dropout Probability: 75.0%" in result
        assert "• Risk Level: High" in result
        assert "• High Risk Flag: Yes" in result
        assert "RECOMMENDATIONS:" in result
        assert (
            "1. Immediate intervention recommended - student is at very high risk"
            in result
        )
