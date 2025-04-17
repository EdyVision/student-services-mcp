import pytest
from src.adapters.clients.registrar import RegistrarSystem
from src.adapters.clients.financial_aid import FinancialAidSystem
from src.adapters.resolvers.financial_aid_resolvers import FinancialAidResolver


class TestFinancialAidResolver:

    @pytest.fixture
    def financial_aid_resolver(self):
        registrar_system = RegistrarSystem(
            "../../../dist/data/synthetic_population_data.csv"
        )
        financial_aid_system = FinancialAidSystem(
            "../../../dist/data/synthetic_financial_aid_determinations.csv"
        )
        return FinancialAidResolver(registrar_system, financial_aid_system)

    @pytest.mark.asyncio
    async def test_resolve_financial_aid_eligibility(
        self, financial_aid_resolver: FinancialAidResolver
    ):
        eligibility = await financial_aid_resolver.resolve_financial_aid_eligibility(
            "d777f2b6-906f-4703-a5f3-efac47766ac0"
        )

        assert eligibility is not None
        assert "Megan Mcclain" in eligibility
        assert "2.84" in eligibility
