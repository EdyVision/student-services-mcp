import pytest
from src.adapters.clients.registrar import RegistrarSystem
from src.adapters.resolvers.registrar_resolvers import RegistrarResolver


class TestRegistarResolver:

    @pytest.fixture
    def registrar_resolver(self):
        return RegistrarResolver(
            RegistrarSystem("../../../dist/data/synthetic_population_data.csv")
        )

    @pytest.mark.asyncio
    async def test_get_student_profile(self, registrar_resolver: RegistrarResolver):
        response = await registrar_resolver.resolve_student_profile(
            "df62674f-5641-4657-a614-901a22ea76f2"
        )
        assert response is not None
        assert "Allison Hill" in response
        assert "2.22" in response

    @pytest.mark.asyncio
    async def test_get_student_profiles(self, registrar_resolver: RegistrarResolver):
        profiles = await registrar_resolver.resolve_student_profiles(10)
        assert len(profiles) == 10
        assert "BIO204" in profiles[1]["courses"]
        assert "HIST300" in profiles[1]["courses"]

    # @pytest.mark.asyncio
    # async def test_get_academic_history(self, resolver):
    #     history = await resolver.resolve_academic_history("df62674f-5641-4657-a614-901a22ea76f2")
    #     assert history is not None
    #     assert history["name"] == "Allison Hill"
    #     assert history["gpa"] == 2.22
