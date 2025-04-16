from typing import Optional
from ..retrievers.base import BaseRetriever


class FAISSRetriever(BaseRetriever):
    def retrieve(self, query: str, metadata: Optional[dict] = None) -> str:
        return f"[FAISS] Retrieved context for: {query}"
