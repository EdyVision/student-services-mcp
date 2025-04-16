# systems/claims.py
import uuid
from datetime import datetime


class ClaimsSystem:
    """Financial Aid Claims System."""

    def __init__(self):
        # Initialize with empty claims
        self.claims = {}

    async def disconnect(self):
        """Disconnect from the claims system."""
        # No actual connections to close in this mock implementation
        pass

    def get_claim_history(self, student_id: str) -> list:
        """Get a student's claim history."""
        return self.claims.get(student_id, [])

    def submit_claim(self, student_id: str, program_id: str, amount: float) -> dict:
        """Submit a new financial aid claim."""
        # Generate a unique claim ID
        claim_id = f"C{uuid.uuid4().hex[:5].upper()}"

        # Create the new claim
        new_claim = {
            "claim_id": claim_id,
            "program_id": program_id,
            "amount": amount,
            "status": "Pending",
            "submitted_date": datetime.now().strftime("%Y-%m-%d"),
            "approved_date": None,
            "term": "Spring 2025",  # Assuming current term
            "notes": "Newly submitted claim",
        }

        # Add to student's claims
        if student_id not in self.claims:
            self.claims[student_id] = []

        self.claims[student_id].append(new_claim)

        return {
            "success": True,
            "claim_id": claim_id,
            "student_id": student_id,
            "program_id": program_id,
            "status": "Pending",
        }
