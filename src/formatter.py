from ..src.templates.default_prompt import build_default_prompt
from ..src.templates.phi4_prompt import build_phi4_prompt


class MCPFormatter:
    def __init__(self, model_type: str = "default"):
        self.model_type = model_type

    def format(self, query: str, retrieved_chunks: list[dict]) -> str:
        if self.model_type == "phi-4":
            return build_phi4_prompt(query, retrieved_chunks)
        return build_default_prompt(query, retrieved_chunks)
