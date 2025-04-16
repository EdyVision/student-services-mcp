import unittest
import os
import pandas as pd
import tempfile

from finaid_admin_mcp_server.src.systems.eligibility import EligibilitySystem


class TestEligibilitySystem(unittest.TestCase):
    """Test the EligibilitySystem component."""

    def setUp(self):
        """Set up test data."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()

        # Create a test CSV file with synthetic data
        self.test_data = [
            {
                "id": "S12345",
                "name": "Test Student",
                "gpa": 3.8,
                "field_of_study": "Computer Science",
                "financial_aid": ["STEM Excellence Award"],
                "requirements": ["GPA ≥ 3.6", "Field of Study in STEM"],
            },
            {
                "id": "S67890",
                "name": "Test Student 2",
                "gpa": 3.2,
                "field_of_study": "Psychology",
                "financial_aid": ["Behavioral and Social Sciences Grant"],
                "requirements": ["Field of Study in Behavioral and Social Sciences"],
            },
        ]

        # Save to CSV
        self.test_csv = os.path.join(self.test_dir, "test_determinations.csv")
        pd.DataFrame(self.test_data).to_csv(self.test_csv, index=False)

        # Initialize system with the test data
        self.eligibility = EligibilitySystem(data_path=self.test_csv)

    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

        # Remove test directory
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_get_eligible_programs(self):
        """Test getting eligible programs for a student."""
        # Test a student with eligibility
        programs = self.eligibility.get_eligible_financial_aid("S12345")
        self.assertEqual(len(programs), 1)
        self.assertEqual(programs[0]["id"], "STEM")

        # Test a student with different eligibility
        programs = self.eligibility.get_eligible_financial_aid("S67890")
        self.assertEqual(len(programs), 1)
        self.assertEqual(programs[0]["id"], "BSSG")

        # Test a student not in the system
        programs = self.eligibility.get_eligible_financial_aid("NONEXISTENT")
        self.assertEqual(len(programs), 0)

    def test_check_specific_eligibility(self):
        """Test checking eligibility for a specific program."""
        # Test eligible student for their program
        result = self.eligibility.check_specific_eligibility("S12345", "STEM")
        self.assertTrue(result["eligible"])

        # Test eligible student for a program they're not eligible for
        result = self.eligibility.check_specific_eligibility("S12345", "BSSG")
        self.assertFalse(result["eligible"])

        # Test nonexistent student
        result = self.eligibility.check_specific_eligibility("NONEXISTENT", "STEM")
        self.assertFalse(result["eligible"])

    def test_get_program_details(self):
        """Test getting program details."""
        # Test existing program
        program = self.eligibility.get_program_details("STEM")
        self.assertEqual(program["name"], "STEM Excellence Award")

        # Test nonexistent program
        program = self.eligibility.get_program_details("NONEXISTENT")
        self.assertIn("error", program)

    def test_determine_financial_aid_eligibility(self):
        """Test the eligibility determination function."""
        # STEM student with high GPA
        requirements, aid = self.eligibility.determine_financial_aid_eligibility(
            3.8, "Computer Science"
        )
        self.assertIn("STEM Excellence Award", aid)
        self.assertIn("GPA ≥ 3.6", requirements)

        # Social sciences student
        requirements, aid = self.eligibility.determine_financial_aid_eligibility(
            3.2, "Psychology"
        )
        self.assertIn("Behavioral and Social Sciences Grant", aid)

        # Law student
        requirements, aid = self.eligibility.determine_financial_aid_eligibility(
            3.0, "Law"
        )
        self.assertIn("Legal Studies Full Ride", aid)

        # Ineligible student
        requirements, aid = self.eligibility.determine_financial_aid_eligibility(
            2.5, "Business"
        )
        self.assertEqual(len(aid), 0)
