# tests/test_systems.py
import unittest
import os
import pandas as pd
import tempfile

from finaid_admin_mcp_server.src.systems.records import RecordsSystem


class TestRecordsSystem(unittest.TestCase):
    """Test the RecordsSystem component."""

    def setUp(self):
        """Set up test data."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()

        # Create a test CSV file with synthetic data
        self.test_data = [
            {
                "student_id": "S12345",
                "name": "Test Student",
                "email": "test@university.edu",
                "phone": "555-123-4567",
                "address": "123 Test St",
                "enrollment_status": "Full-time",
                "major": "Computer Science",
                "year": "Junior",
                "gpa": 3.8,
                "financial_status": "{'efc': 0, 'dependency_status': 'Independent', 'household_income': 25000, 'household_size': 1}",
            }
        ]

        # Save to CSV
        self.test_csv = os.path.join(self.test_dir, "test_population.csv")
        pd.DataFrame(self.test_data).to_csv(self.test_csv, index=False)

        # Initialize system with the test data
        self.records = RecordsSystem(data_path=self.test_csv)

    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

        # Remove test directory
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_get_student_profile(self):
        """Test getting a student's profile."""
        # Test existing student
        profile = self.records.get_student_profile("S12345")
        self.assertEqual(profile["name"], "Test Student")
        self.assertEqual(profile["major"], "Computer Science")

        # Test nonexistent student
        profile = self.records.get_student_profile("NONEXISTENT")
        self.assertIn("error", profile)

    def test_get_academic_history(self):
        """Test getting a student's academic history."""
        # Test existing student
        history = self.records.get_academic_history("S12345")
        self.assertIn("courses", history)
        self.assertIn("credits_attempted", history)
        self.assertIn("credits_earned", history)

        # Test that GPA is reflected in the courses
        if history["courses"]:
            # Check that there are some courses with A grades for a high GPA student
            a_grades = [c for c in history["courses"] if c["grade"].startswith("A")]
            self.assertTrue(len(a_grades) > 0)

        # Test nonexistent student
        history = self.records.get_academic_history("NONEXISTENT")
        self.assertIn("error", history)
