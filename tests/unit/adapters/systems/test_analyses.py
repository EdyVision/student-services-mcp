import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from src.adapters.systems.analyses import StudentAnalysesSystem


class TestStudentAnalysesSystem:
    """Test cases for StudentAnalysesSystem."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame(
            {
                "student_id": ["S001", "S002", "S003"],
                "name": ["Alice", "Bob", "Charlie"],
                "gpa": [3.5, 2.1, 3.8],
                "major": ["Computer Science", "Mathematics", "Biology"],
                "year": ["Sophomore", "Junior", "Freshman"],
                "work_hours": [20, 35, 10],
                "semesters_completed": [2, 3, 1],
                "credits_attempted": [30, 45, 15],
                "credits_completed": [30, 20, 15],
                "completion_rate": [1.0, 0.44, 1.0],
                "failed_courses": [0, 5, 0],
                "withdrawn_courses": [0, 2, 0],
                "gpa_trend": ["stable", "declining", "improving"],
                "attendance_rate": [0.95, 0.75, 0.98],
                "stress_frequency": [1, 3, 0],
                "course_load_variance": [0.0, 25.0, 0.0],
                "graduation_timeline_risk": ["on_track", "delayed", "on_track"],
                "dropped_out": [False, True, False],
                "dropout_encoded": [0, 1, 0],
                "dropout_risk": [False, True, False],
                "dropout_probability": [0.25, 0.85, 0.15],
            }
        )

    @pytest.fixture
    def mock_csv_path(self, tmp_path, sample_data):
        """Create a mock CSV file for testing."""
        csv_path = tmp_path / "test_data.csv"
        sample_data.to_csv(csv_path, index=False)
        return str(csv_path)

    @pytest.fixture
    def analyses_system(self, mock_csv_path):
        """Create an analyses system with test data."""
        return StudentAnalysesSystem(mock_csv_path)

    def test_initialization_with_data(self, analyses_system):
        """Test system initialization with data."""
        assert len(analyses_system.students) == 3
        assert len(analyses_system.attrition_features) == 3
        assert "S001" in analyses_system.students
        assert "S001" in analyses_system.attrition_features

    def test_initialization_without_data(self):
        """Test system initialization without data file."""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                StudentAnalysesSystem("nonexistent.csv")

    def test_calculate_attrition_features(self, analyses_system):
        """Test attrition features calculation."""
        student = {
            "gpa": 3.5,
            "work_hours": 20,
            "major": "Computer Science",
            "year": "Sophomore",
            "past_terms": [
                {
                    "credits": 15,
                    "courses": [
                        {"grade": "A", "credits": 3},
                        {"grade": "B+", "credits": 3},
                        {"grade": "A-", "credits": 3},
                        {"grade": "B", "credits": 3},
                        {"grade": "A", "credits": 3},
                    ],
                    "stress": "moderate",
                }
            ],
        }

        features = analyses_system.calculate_attrition_features(student)

        assert features["semesters_completed"] == 1
        assert features["credits_attempted"] == 15
        assert features["credits_completed"] == 15
        assert features["completion_rate"] == 1.0
        assert features["failed_courses"] == 0
        assert features["withdrawn_courses"] == 0
        assert features["stress_frequency"] == 0

    def test_calculate_dropout_probability_low_risk(self, analyses_system):
        """Test dropout probability calculation for low-risk student."""
        student = {"gpa": 3.8, "work_hours": 10, "year": "Senior"}
        attrition_features = {
            "completion_rate": 0.95,
            "failed_courses": 0,
            "withdrawn_courses": 0,
            "gpa_trend": "improving",
            "attendance_rate": 0.98,
            "stress_frequency": 0,
            "course_load_variance": 5.0,
            "graduation_timeline_risk": "on_track",
        }

        probability = analyses_system.calculate_dropout_probability(
            student, attrition_features
        )

        assert 0.0 <= probability <= 1.0
        assert probability < 0.5  # Should be low risk

    def test_calculate_dropout_probability_high_risk(self, analyses_system):
        """Test dropout probability calculation for high-risk student."""
        student = {"gpa": 2.0, "work_hours": 40, "year": "Freshman"}
        attrition_features = {
            "completion_rate": 0.6,
            "failed_courses": 5,
            "withdrawn_courses": 3,
            "gpa_trend": "declining",
            "attendance_rate": 0.7,
            "stress_frequency": 4,
            "course_load_variance": 60.0,
            "graduation_timeline_risk": "delayed",
        }

        probability = analyses_system.calculate_dropout_probability(
            student, attrition_features
        )

        assert 0.0 <= probability <= 1.0
        assert probability > 0.5  # Should be high risk

    @pytest.mark.asyncio
    async def test_predict_dropout_risk_success(self, analyses_system):
        """Test successful dropout risk prediction."""
        result = await analyses_system.predict_dropout_risk("S001")

        assert "student_id" in result
        assert "name" in result
        assert "dropout_probability" in result
        assert "dropout_risk" in result
        assert "risk_level" in result
        assert "attrition_features" in result
        assert "recommendations" in result
        assert result["student_id"] == "S001"
        assert result["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_predict_dropout_risk_student_not_found(self, analyses_system):
        """Test dropout risk prediction for non-existent student."""
        result = await analyses_system.predict_dropout_risk("S999")

        assert "error" in result
        assert result["error"] == "Student not found"

    @pytest.mark.asyncio
    async def test_get_high_risk_students(self, analyses_system):
        """Test getting high-risk students."""
        students = await analyses_system.get_high_risk_students(limit=2)

        assert len(students) <= 2
        for student in students:
            assert "student_id" in student
            assert "name" in student
            assert "dropout_probability" in student
            assert student["dropout_probability"] > 0.4  # High risk threshold

    @pytest.mark.asyncio
    async def test_get_attrition_statistics(self, analyses_system):
        """Test getting attrition statistics."""
        stats = await analyses_system.get_attrition_statistics()

        assert "total_students" in stats
        assert "dropout_count" in stats
        assert "dropout_rate" in stats
        assert "high_risk_count" in stats
        assert "high_risk_rate" in stats
        assert "average_dropout_probability" in stats
        assert "dropout_by_year" in stats
        assert stats["total_students"] == 3

    @pytest.mark.asyncio
    async def test_get_attrition_feature_importance(self, analyses_system):
        """Test getting attrition feature importance analysis."""
        analysis = await analyses_system.get_attrition_feature_importance()

        assert "correlation_analysis" in analysis
        assert "model_importance" in analysis
        assert "categorical_analysis" in analysis
        assert "total_students_analyzed" in analysis
        assert "insights" in analysis
        assert analysis["total_students_analyzed"] == 3

    @pytest.mark.asyncio
    async def test_get_attrition_feature_importance_no_data(self):
        """Test feature importance analysis with no data."""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                system = StudentAnalysesSystem("nonexistent.csv")

    def test_generate_recommendations_high_risk(self, analyses_system):
        """Test recommendation generation for high-risk student."""
        attrition_features = {
            "completion_rate": 0.6,
            "failed_courses": 5,
            "attendance_rate": 0.7,
            "stress_frequency": 4,
            "gpa_trend": "declining",
            "graduation_timeline_risk": "delayed",
        }

        recommendations = analyses_system._generate_recommendations(
            attrition_features, 0.8
        )

        assert len(recommendations) > 0
        assert any("immediate intervention" in rec.lower() for rec in recommendations)
        assert any("course completion" in rec.lower() for rec in recommendations)
        assert any("multiple course failures" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_low_risk(self, analyses_system):
        """Test recommendation generation for low-risk student."""
        attrition_features = {
            "completion_rate": 0.95,
            "failed_courses": 0,
            "attendance_rate": 0.98,
            "stress_frequency": 0,
            "gpa_trend": "improving",
            "graduation_timeline_risk": "on_track",
        }

        recommendations = analyses_system._generate_recommendations(
            attrition_features, 0.2
        )

        assert len(recommendations) > 0
        assert any("on track" in rec.lower() for rec in recommendations)

    def test_generate_feature_insights(self, analyses_system):
        """Test feature insights generation."""
        sorted_features = [("gpa", 0.5), ("completion_rate", 0.4)]
        gpa_trend_dropout = {"declining": 0.7, "stable": 0.4}
        timeline_dropout = {"delayed": 0.6, "on_track": 0.2}

        insights = analyses_system._generate_feature_insights(
            sorted_features, gpa_trend_dropout, timeline_dropout
        )

        assert len(insights) > 0
        assert any("gpa" in insight.lower() for insight in insights)
        assert any("declining" in insight.lower() for insight in insights)

    @pytest.mark.asyncio
    async def test_disconnect(self, analyses_system):
        """Test system disconnect."""
        # Should not raise any exceptions
        await analyses_system.disconnect()
