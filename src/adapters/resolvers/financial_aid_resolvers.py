from src.adapters.clients.financial_aid import FinancialAidSystem
from src.adapters.clients.registrar import RegistrarSystem


class FinancialAidResolver:
    """Resolver for Financial Aid System."""

    def __init__(self, registrar: RegistrarSystem, financial_aid: FinancialAidSystem):
        self.financial_aid_system = financial_aid
        self.registrar_system = registrar

    async def resolve_financial_aid_eligibility(self, student_id: str) -> str:
        """Resolve a student's financial aid eligibility."""
        profile = await self.registrar_system.get_student_profile(student_id)

        if not profile:
            return f"Student with ID {student_id} not found."

        requirements, financial_aid = (
            await self.financial_aid_system.get_eligible_financial_aid(profile)
        )

        if financial_aid:
            return f"Student {profile['name']} (ID: {student_id}) has a GPA of {profile['gpa']} in {profile['major']}. They are eligible for the {financial_aid}. Requirements: {requirements}"
        else:
            return f"Student {profile['name']} (ID: {student_id}) has a GPA of {profile['gpa']} in {profile['major']}. They are not eligible for financial aid. Requirements: {requirements if requirements else 'Requirements unspecified for program or major.'}"
