from typing import Optional

from ..retrievers.base import BaseRetriever


class DynamoDBRetriever(BaseRetriever):
    def retrieve(self, query: str, metadata: Optional[dict] = None) -> str:
        return f"[DynamoDB] Retrieved context for: {query}"
