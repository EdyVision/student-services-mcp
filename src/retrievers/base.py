from abc import ABC, abstractmethod
from typing import Optional


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, metadata: Optional[dict] = None) -> str:
        """Retrieve context from a source"""
        pass
