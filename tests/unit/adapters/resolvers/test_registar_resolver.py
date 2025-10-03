import pytest
import pandas as pd
import json
import os
from src.adapters.systems.registrar import RegistrarSystem
from src.adapters.resolvers.registrar_resolvers import RegistrarResolver

DATA_PATH = os.path.join(
    os.path.dirname(__file__), "../../../dist/data/synthetic_population_data.csv"
)


class TestRegistarResolver:

    @pytest.fixture(scope="module")
    def student_data(self):
        df = pd.read_csv(DATA_PATH)
        # Parse the first row for a real student
        student = df.iloc[0]
        student_id = student["student_id"]
        name = student["name"]
        gpa = str(student["gpa"])
        # Parse past_terms JSON to get a real course code
        past_terms = json.loads(student["past_terms"])
        course_code = (
            past_terms[0]["courses"][0]["course_code"]
            if past_terms and past_terms[0]["courses"]
            else None
        )
        return {
            "student_id": student_id,
            "name": name,
            "gpa": gpa,
            "course_code": course_code,
        }

    @pytest.fixture
    def registrar_resolver(self):
        return RegistrarResolver(RegistrarSystem(DATA_PATH))

    @pytest.mark.asyncio
    async def test_get_student_profile(self, registrar_resolver, student_data):
        response = await registrar_resolver.resolve_student_profile(
            student_data["student_id"]
        )
        assert response is not None
        assert student_data["name"] in response
        assert student_data["gpa"] in response

    @pytest.mark.asyncio
    async def test_get_student_profiles(self, registrar_resolver, student_data):
        profiles = await registrar_resolver.resolve_student_profiles(10)
        assert len(profiles) == 10

        def has_course(profile, code):
            return any(
                course["course_code"] == code
                for term in profile["past_terms"]
                for course in term["courses"]
            )

        # Use the first profile and the real course code
        assert has_course(profiles[0], student_data["course_code"])

    @pytest.mark.asyncio
    async def test_get_student_profile_missing(
        self, registrar_resolver: RegistrarResolver
    ):
        response = await registrar_resolver.resolve_student_profile("FAKE_ID")
        assert response == "Student with ID FAKE_ID not found."

    @pytest.mark.asyncio
    async def test_resolve_academic_history(
        self, registrar_resolver: RegistrarResolver
    ):
        # Should return error since academic history is not populated
        response = await registrar_resolver.resolve_academic_history("S3CC01")
        assert "error" in response
        response_missing = await registrar_resolver.resolve_academic_history("FAKE_ID")
        assert "error" in response_missing

    @pytest.mark.asyncio
    async def test_submit_note_success_and_failure(
        self, registrar_resolver, student_data
    ):
        # Success
        response = await registrar_resolver.submit_note(
            student_data["student_id"], "Great progress", "low"
        )
        assert "Successfully added note" in response
        # Failure
        response_fail = await registrar_resolver.submit_note("FAKE_ID", "Note", "high")
        assert response_fail == "Student with ID FAKE_ID not found."

    @pytest.mark.asyncio
    async def test_generate_course_plan_success_and_missing(
        self, registrar_resolver, student_data
    ):
        # Success
        response = await registrar_resolver.generate_course_plan(
            student_data["student_id"], 12, "low"
        )
        assert f"Course plan for {student_data['name']}" in response
        # Missing student
        response_missing = await registrar_resolver.generate_course_plan(
            "FAKE_ID", 12, "low"
        )
        assert response_missing == "Student with ID FAKE_ID not found."

    @pytest.mark.asyncio
    async def test_submit_course_plan_success_and_missing(
        self, registrar_resolver, student_data
    ):
        # Success
        response = await registrar_resolver.submit_course_plan(
            student_data["student_id"], "Plan details", "Because it is required"
        )
        assert "Successfully submitted course plan" in response
        # Missing student
        response_missing = await registrar_resolver.submit_course_plan(
            "FAKE_ID", "Plan", "Justification"
        )
        assert response_missing == "Student with ID FAKE_ID not found."

    def test_determine_need_based_status(self, registrar_resolver: RegistrarResolver):
        # True
        assert (
            registrar_resolver._RegistrarResolver__determine_need_based_status(True)
            == "qualifies for need-based aid"
        )
        # False
        assert (
            registrar_resolver._RegistrarResolver__determine_need_based_status(False)
            == "does not qualify for need-based aid"
        )
