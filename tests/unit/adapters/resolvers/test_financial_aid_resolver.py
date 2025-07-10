import pytest
import pandas as pd
import json
from src.adapters.clients.registrar import RegistrarSystem
from src.adapters.clients.financial_aid import FinancialAidSystem
from src.adapters.resolvers.financial_aid_resolvers import FinancialAidResolver
import os
import pandas as pd
from src.adapters.clients.synthetic_data import build_synthetic_data


@pytest.fixture(scope="module")
def student_data():
    data_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../../dist/data/synthetic_population_data.csv",
        )
    )
    # Generate the data if it doesn't exist
    if not os.path.exists(data_path):
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        build_synthetic_data(num_students=50, directory=os.path.dirname(data_path))
    df = pd.read_csv(data_path)
    student = df.iloc[0]
    student_id = student["student_id"]
    name = student["name"]
    gpa = str(student["gpa"])
    return {
        "student_id": student_id,
        "name": name,
        "gpa": gpa,
    }


class TestFinancialAidResolver:

    @pytest.fixture
    def financial_aid_resolver(self):
        data_path = os.path.join(
            os.path.dirname(__file__),
            "../../../dist/data/synthetic_population_data.csv",
        )
        registrar_system = RegistrarSystem(data_path)
        financial_aid_system = FinancialAidSystem()
        return FinancialAidResolver(registrar_system, financial_aid_system)

    @pytest.mark.asyncio
    async def test_resolve_financial_aid_eligibility(
        self, financial_aid_resolver: FinancialAidResolver, student_data
    ):
        eligibility = await financial_aid_resolver.resolve_financial_aid_eligibility(
            student_data["student_id"]
        )

        assert eligibility is not None
        assert student_data["name"] in eligibility
        assert student_data["gpa"] in eligibility
