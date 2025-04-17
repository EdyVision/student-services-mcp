import os
import pandas as pd


class FinancialAidSystem:
    """Financial Aid Eligibility System using synthetic data."""

    def __init__(
        self, data_path="dist/data/synthetic_financial_aid_determinations.csv"
    ):
        # Load synthetic data
        self.synthetic_data = {}
        if os.path.exists(data_path):
            try:
                df = pd.read_csv(data_path)
                # Convert dataframe to dictionary keyed by student ID
                for _, row in df.iterrows():
                    # Convert lists stored as strings back to actual lists
                    financial_aid = (
                        eval(row["financial_aid"])
                        if isinstance(row["financial_aid"], str)
                        else row["financial_aid"]
                    )
                    requirements = (
                        eval(row["requirements"])
                        if isinstance(row["requirements"], str)
                        else row["requirements"]
                    )

                    self.synthetic_data[row["id"]] = {
                        "id": row["id"],
                        "name": row["name"],
                        "gpa": row["gpa"],
                        "field_of_study": row["field_of_study"],
                        "financial_aid": financial_aid,
                        "requirements": requirements,
                    }
            except Exception as e:
                print(f"Error loading synthetic data: {e}")
                self.synthetic_data = {}

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
            "LSFR": {
                "id": "LSFR",
                "name": "Legal Studies Full Ride",
                "description": "Full tuition coverage for legal studies students.",
                "max_amount": 10000.00,
                "criteria": "Field of Study in Legal Studies.",
                "deadline": "April 30, 2025",
            },
        }

        # Map program names to IDs
        self.program_name_to_id = {
            "STEM Excellence Award": "STEM",
            "Behavioral and Social Sciences Grant": "BSSG",
            "Legal Studies Full Ride": "LSFR",
        }

    async def get_eligible_financial_aid(self, student: dict):
        """Get all aid options a student is eligible for."""
        # Try to find student in synthetic data
        if student and student["student_id"] in self.synthetic_data:
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

        if field_of_study in [
            "Computer Science",
            "Engineering",
            "Mathematics",
            "IT",
            "Statistics",
        ]:
            financial_aid.append("STEM Excellence Award")
            requirements.append("Field of Study in STEM")

        if field_of_study in ["Psychology", "Sociology", "Social Work", "Anthropology"]:
            financial_aid.append("Behavioral and Social Sciences Grant")
            requirements.append("Field of Study in Behavioral and Social Sciences")

        if field_of_study in ["Paralegal", "Law"]:
            financial_aid.append("Legal Studies Full Ride")
            requirements.append("Field of Study in Legal Studies")

        return requirements, financial_aid

    async def disconnect(self):
        """Disconnect from the eligibility system."""
        # No actual connections to close in this mock implementation
        pass
