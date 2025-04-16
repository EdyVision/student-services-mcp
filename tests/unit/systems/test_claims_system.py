import unittest

from finaid_admin_mcp_server.src.systems.claims import ClaimsSystem


class TestClaimsSystem(unittest.TestCase):
    """Test the ClaimsSystem component."""

    def setUp(self):
        """Set up test data."""
        self.claims = ClaimsSystem()

    def test_submit_claim(self):
        """Test submitting a new claim."""
        # Submit a claim
        result = self.claims.submit_claim("S12345", "STEM", 5000.0)

        # Check the result
        self.assertTrue(result["success"])
        self.assertEqual(result["student_id"], "S12345")
        self.assertEqual(result["program_id"], "STEM")
        self.assertEqual(result["status"], "Pending")

        # Check that the claim was stored
        claims = self.claims.get_claim_history("S12345")
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0]["program_id"], "STEM")
        self.assertEqual(claims[0]["amount"], 5000.0)

    def test_get_claim_history(self):
        """Test getting a student's claim history."""
        # Submit some claims
        self.claims.submit_claim("S12345", "STEM", 5000.0)
        self.claims.submit_claim("S12345", "BSSG", 4000.0)

        # Get history
        history = self.claims.get_claim_history("S12345")

        # Check the history
        self.assertEqual(len(history), 2)

        # Check that getting history for a student with no claims returns empty list
        history = self.claims.get_claim_history("NONEXISTENT")
        self.assertEqual(len(history), 0)
