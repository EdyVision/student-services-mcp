from typing import List
import json
from src.adapters.clients.registrar import RegistrarSystem


class RegistrarResolver:
    """Resolver for Registrar System."""

    def __init__(self, registrar: RegistrarSystem):
        self.registrar = registrar

    async def resolve_student_profile(self, student_id: str) -> str:
        """Resolve a student's profile."""
        profile = await self.registrar.get_student_profile(student_id)

        if not profile or "error" in profile:
            return f"Student with ID {student_id} not found."

        return f"Student {profile['name']} (ID: {student_id}) has a GPA of {profile['gpa']} in {profile['major']} and {self.__determine_need_based_status(bool(profile['is_need_based_qualified']))}."

    async def resolve_student_profile_by_name(self, student_name: str) -> str:
        """Resolve a student's profile by name."""
        return await self.registrar.get_student_profile_by_name(student_name)

    async def resolve_student_profiles(self, limit: int = 100) -> List[str]:
        """Resolve a list of student profiles."""
        return await self.registrar.get_student_profiles(limit)

    async def resolve_academic_history(self, student_id: str) -> str:
        """Resolve a student's academic history."""
        return await self.registrar.get_academic_history(student_id)

    async def submit_note(self, student_id: str, note: str, stress_level: str) -> str:
        """Submit a note and stress level for a student."""
        profile = await self.registrar.get_student_profile(student_id)

        if not profile or "error" in profile:
            return f"Student with ID {student_id} not found."

        # Add the note to the student's notes array
        result = await self.registrar.add_note(student_id, note, stress_level)

        if result:
            return f"Successfully added note for student {profile['name']} (ID: {student_id}). Current stress level: {stress_level}"
        else:
            return f"Student with ID {student_id} not found."

    async def generate_course_plan(
        self, student_id: str, target_credits: int, stress_level: str
    ) -> str:
        """Generate a course plan based on stress level and target credits."""
        profile = await self.registrar.get_student_profile(student_id)

        if not profile or "error" in profile:
            return f"Student with ID {student_id} not found."

        # Generate course plan based on stress level and target credits
        course_plan = await self.registrar.generate_course_plan(
            student_id, target_credits, stress_level
        )

        return f"Course plan for {profile['name']} (ID: {student_id}):\n{course_plan}"

    async def submit_course_plan(
        self, student_id: str, plan: str, justification: str
    ) -> str:
        """Submit a course plan with justification."""
        profile = await self.registrar.get_student_profile(student_id)

        if not profile or "error" in profile:
            return f"Student with ID {student_id} not found."

        # Submit the course plan
        result = await self.registrar.submit_course_plan(
            student_id, plan, justification
        )

        if result:
            return f"Successfully submitted course plan for student {profile['name']} (ID: {student_id}). Justification: {justification}"
        else:
            return f"Student with ID {student_id} not found."

    def __determine_need_based_status(self, need_based_qualified: bool) -> str:
        return (
            "qualifies for need-based aid"
            if need_based_qualified
            else "does not qualify for need-based aid"
        )
