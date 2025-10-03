import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from src.adapters.systems.synthetic_data import (
    generate_student,
    calculate_attrition_features,
    generate_dropout_labels,
    determine_financial_aid_eligibility,
    build_synthetic_data,
    split_data_and_save,
)


class TestSyntheticDataFunctions:
    """Test cases for synthetic data generation functions."""

    def test_generate_student(self):
        """Test student generation."""
        student = generate_student()

        assert "student_id" in student
        assert "name" in student
        assert "gpa" in student
        assert "major" in student
        assert "year" in student
        assert "work_hours" in student
        assert "semesters_completed" in student
        assert "credits_attempted" in student
        assert "credits_completed" in student
        assert "completion_rate" in student
        assert "failed_courses" in student
        assert "withdrawn_courses" in student
        assert "gpa_trend" in student
        assert "attendance_rate" in student
        assert "stress_frequency" in student
        assert "course_load_variance" in student
        assert "graduation_timeline_risk" in student
        assert "dropped_out" in student
        assert "dropout_encoded" in student
        assert "dropout_risk" in student
        assert "dropout_probability" in student

    def test_generate_student_data_types(self):
        """Test that generated student has correct data types."""
        student = generate_student()

        assert isinstance(student["student_id"], str)
        assert isinstance(student["name"], str)
        assert isinstance(student["gpa"], (int, float))
        assert isinstance(student["major"], str)
        assert isinstance(student["year"], str)
        assert isinstance(student["work_hours"], int)
        assert isinstance(student["semesters_completed"], int)
        assert isinstance(student["credits_attempted"], int)
        assert isinstance(student["credits_completed"], int)
        assert isinstance(student["completion_rate"], (int, float))
        assert isinstance(student["failed_courses"], int)
        assert isinstance(student["withdrawn_courses"], int)
        assert isinstance(student["gpa_trend"], str)
        assert isinstance(student["attendance_rate"], (int, float))
        assert isinstance(student["stress_frequency"], int)
        assert isinstance(student["course_load_variance"], (int, float))
        assert isinstance(student["graduation_timeline_risk"], str)
        assert isinstance(student["dropped_out"], bool)
        assert isinstance(student["dropout_encoded"], int)
        assert isinstance(student["dropout_risk"], bool)
        assert isinstance(student["dropout_probability"], (int, float))

    def test_generate_student_ranges(self):
        """Test that generated student data is within expected ranges."""
        student = generate_student()

        assert 0.0 <= student["gpa"] <= 4.0
        assert 0 <= student["work_hours"] <= 40
        assert 1 <= student["semesters_completed"] <= 8
        assert 0 <= student["credits_attempted"] <= 150
        assert 0 <= student["credits_completed"] <= 150
        assert 0.0 <= student["completion_rate"] <= 1.0
        assert 0 <= student["failed_courses"] <= 20
        assert 0 <= student["withdrawn_courses"] <= 10
        assert student["gpa_trend"] in ["improving", "stable", "declining"]
        assert 0.0 <= student["attendance_rate"] <= 1.0
        assert 0 <= student["stress_frequency"] <= 5
        assert 0.0 <= student["course_load_variance"] <= 100.0
        assert student["graduation_timeline_risk"] in ["on_track", "delayed", "at_risk"]
        assert student["dropout_encoded"] in [0, 1]
        assert 0.0 <= student["dropout_probability"] <= 1.0

    def test_calculate_attrition_features(self):
        """Test attrition features calculation."""
        past_terms = [
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
        ]

        features = calculate_attrition_features(
            past_terms,
            3.5,
            20,
            {"household_income": 50000, "efc": 5000},
            "Computer Science",
            "Sophomore",
        )

        assert "semesters_completed" in features
        assert "credits_attempted" in features
        assert "credits_completed" in features
        assert "completion_rate" in features
        assert "failed_courses" in features
        assert "withdrawn_courses" in features
        assert "gpa_trend" in features
        assert "attendance_rate" in features
        assert "stress_frequency" in features
        assert "course_load_variance" in features
        assert "graduation_timeline_risk" in features

    def test_generate_dropout_labels(self):
        """Test dropout labels generation."""
        attrition_features = {
            "completion_rate": 0.8,
            "failed_courses": 2,
            "withdrawn_courses": 1,
            "gpa_trend": "stable",
            "attendance_rate": 0.9,
            "stress_frequency": 2,
            "course_load_variance": 10.0,
            "graduation_timeline_risk": "on_track",
        }

        labels = generate_dropout_labels(
            attrition_features,
            3.0,
            25,
            {"household_income": 50000, "efc": 5000},
            "Mathematics",
            "Junior",
        )

        assert "dropped_out" in labels
        assert "dropout_encoded" in labels
        assert "dropout_risk" in labels
        assert "dropout_probability" in labels
        assert isinstance(labels["dropped_out"], bool)
        assert labels["dropout_encoded"] in [0, 1]
        assert isinstance(labels["dropout_risk"], bool)
        assert 0.0 <= labels["dropout_probability"] <= 1.0

    def test_generate_dropout_labels_high_risk(self):
        """Test dropout labels generation for high-risk student."""
        attrition_features = {
            "completion_rate": 0.5,
            "failed_courses": 8,
            "withdrawn_courses": 5,
            "gpa_trend": "declining",
            "attendance_rate": 0.6,
            "stress_frequency": 5,
            "course_load_variance": 80.0,
            "graduation_timeline_risk": "delayed",
        }

        labels = generate_dropout_labels(
            attrition_features,
            1.8,
            40,
            {"household_income": 20000, "efc": 15000},
            "Biology",
            "Freshman",
        )

        # High-risk student should have higher dropout probability
        assert labels["dropout_probability"] > 0.5

    def test_generate_dropout_labels_low_risk(self):
        """Test dropout labels generation for low-risk student."""
        attrition_features = {
            "completion_rate": 0.98,
            "failed_courses": 0,
            "withdrawn_courses": 0,
            "gpa_trend": "improving",
            "attendance_rate": 0.99,
            "stress_frequency": 0,
            "course_load_variance": 2.0,
            "graduation_timeline_risk": "on_track",
        }

        labels = generate_dropout_labels(
            attrition_features,
            3.8,
            5,
            {"household_income": 80000, "efc": 2000},
            "Computer Science",
            "Senior",
        )

        # Low-risk student should have lower dropout probability
        assert labels["dropout_probability"] < 0.5

    def test_determine_financial_aid_eligibility_high_gpa(self):
        """Test financial aid eligibility for high GPA student."""
        requirements, financial_aid = determine_financial_aid_eligibility(
            3.9, "Computer Science"
        )

        assert len(financial_aid) > 0
        assert "Presidential Scholarship" in financial_aid
        assert "STEM Excellence Award" in financial_aid
        assert "GPA ≥ 3.8" in requirements

    def test_determine_financial_aid_eligibility_stem_field(self):
        """Test financial aid eligibility for STEM field."""
        requirements, financial_aid = determine_financial_aid_eligibility(
            3.5, "Engineering"
        )

        assert "STEM Excellence Award" in financial_aid
        assert "Field of Study in STEM" in requirements

    def test_determine_financial_aid_eligibility_low_gpa(self):
        """Test financial aid eligibility for low GPA student."""
        requirements, financial_aid = determine_financial_aid_eligibility(
            2.8, "History"
        )

        # Should get need-based aid if no merit aid
        assert len(financial_aid) > 0
        assert (
            "Need-Based Grant" in financial_aid
            or "Liberal Arts Fellowship" in financial_aid
        )

    def test_determine_financial_aid_eligibility_business_field(self):
        """Test financial aid eligibility for business field."""
        requirements, financial_aid = determine_financial_aid_eligibility(
            3.3, "Business"
        )

        assert "Business Leadership Scholarship" in financial_aid
        assert "Field of Study in Business/Economics" in requirements

    @patch("os.makedirs")
    @patch("pandas.DataFrame.to_csv")
    def test_build_synthetic_data(self, mock_to_csv, mock_makedirs):
        """Test building synthetic data."""
        students, financial_aid = build_synthetic_data(num_students=5)

        assert len(students) == 5
        assert len(financial_aid) == 5
        assert mock_makedirs.called
        assert mock_to_csv.call_count == 2  # Called twice for both CSVs

    @patch("pandas.read_csv")
    @patch("pandas.DataFrame.to_csv")
    def test_split_data_and_save(self, mock_to_csv, mock_read_csv):
        """Test splitting data and saving."""
        # Mock the CSV data with more rows to ensure proper splitting
        mock_data = pd.DataFrame(
            {
                "id": [f"S{i:03d}" for i in range(10)],
                "name": [f"Student{i}" for i in range(10)],
                "gpa": [3.0 + (i % 3) * 0.3 for i in range(10)],
            }
        )
        mock_read_csv.return_value = mock_data

        train, val, test = split_data_and_save()

        assert len(train) > 0
        assert len(val) >= 0  # val might be empty with small datasets
        assert len(test) >= 0  # test might be empty with small datasets
        assert len(train) + len(val) + len(test) == 10
        assert mock_to_csv.call_count == 3  # Called for train, val, test
