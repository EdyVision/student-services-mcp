from typing import Optional

from ..retrievers.base import BaseRetriever


class S3Retriever(BaseRetriever):
    def retrieve(self, query: str, metadata: Optional[dict] = None) -> str:
        return f"[S3] Retrieved context for: {query}"
