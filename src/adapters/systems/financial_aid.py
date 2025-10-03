import os
import pandas as pd


class FinancialAidSystem:
    """Financial Aid Eligibility System using synthetic data."""

    def __init__(self):

        # Define program details
        self.programs = {
            "STEM": {
                "id": "STEM",
                "name": "STEM Excellence Award",
                "description": "Financial aid for students in STEM fields.",
                "max_amount": 5000.00,
                "criteria": "Field of Study in STEM and minimum GPA of 3.6.",
                "deadline": "May 31, 2025",
            },
            "BSSG": {
                "id": "BSSG",
                "name": "Behavioral and Social Sciences Grant",
                "description": "Grant program for behavioral and social sciences students.",
                "max_amount": 4000.00,
                "criteria": "Field of Study in Behavioral and Social Sciences.",
                "deadline": "June 15, 2025",
            },
            "HES": {
                "id": "HES",
                "name": "Humanities Excellence Scholarship",
                "description": "Scholarship program for humanities and arts students.",
                "max_amount": 4500.00,
                "criteria": "Field of Study in Humanities.",
                "deadline": "June 30, 2025",
            },
        }

        # Map program names to IDs
        self.program_name_to_id = {
            "STEM Excellence Award": "STEM",
            "Behavioral and Social Sciences Grant": "BSSG",
            "Humanities Excellence Scholarship": "HES",
        }

    async def get_eligible_financial_aid(self, student: dict):
        """Get all aid options a student is eligible for."""
        # Try to find student in synthetic data
        if student and student["student_id"]:
            requirements, financial_aid = self.determine_financial_aid_eligibility(
                student["gpa"], student["major"]
            )

            return requirements, financial_aid

        # If student not in synthetic data, return empty tuple
        return None, None

    @staticmethod
    def determine_financial_aid_eligibility(gpa, field_of_study):
        """
        Uses a student record to determine coverage against defined parameters
        """
        financial_aid = []
        requirements = []

        if gpa >= 3.6:
            requirements.append("GPA ≥ 3.6")

        # STEM Fields
        if field_of_study in [
            "Computer Science",
            "Engineering",
            "Mathematics",
            "IT",
            "Statistics",
            "Biology",
            "Nursing",
        ]:
            financial_aid.append("STEM Excellence Award")
            requirements.append("Field of Study in STEM")

        # Behavioral and Social Sciences
        if field_of_study in [
            "Psychology",
            "Sociology",
            "Social Work",
            "Anthropology",
            "Economics",
        ]:
            financial_aid.append("Behavioral and Social Sciences Grant")
            requirements.append("Field of Study in Behavioral and Social Sciences")

        # Humanities and Arts (New Category)
        if field_of_study in [
            "English Literature",
            "Creative Writing",
            "Comparative Literature",
        ]:
            financial_aid.append("Humanities Excellence Scholarship")
            requirements.append("Field of Study in Humanities")

        # If no specific program matches
        if not financial_aid:
            requirements.append("Requirements unspecified for program or major")

        return requirements, financial_aid

    async def disconnect(self):
        """Disconnect from the eligibility system."""
        # No actual connections to close in this mock implementation
        pass
