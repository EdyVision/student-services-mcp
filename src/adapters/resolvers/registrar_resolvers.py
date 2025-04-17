from typing import List
from src.adapters.clients.registrar import RegistrarSystem


class RegistrarResolver:
    """Resolver for Registrar System."""

    def __init__(self, registrar: RegistrarSystem):
        self.registrar = registrar

    async def resolve_student_profile(self, student_id: str) -> str:
        """Resolve a student's profile."""
        profile = await self.registrar.get_student_profile(student_id)

        if not profile:
            return f"Student with ID {student_id} not found."

        return f"Student {profile['name']} (ID: {student_id}) has a GPA of {profile['gpa']} in {profile['major']} and {self.__determine_need_based_status(bool(profile['is_need_based_qualified']))}."

    async def resolve_student_profiles(self, limit: int = 100) -> List[str]:
        """Resolve a list of student profiles."""
        return await self.registrar.get_student_profiles(limit)

    async def resolve_academic_history(self, student_id: str) -> str:
        """Resolve a student's academic history."""
        return await self.registrar.get_academic_history(student_id)

    def __determine_need_based_status(self, need_based_qualified: bool) -> str:
        return (
            "qualifies for need-based aid"
            if need_based_qualified
            else "does not qualify for need-based aid"
        )
