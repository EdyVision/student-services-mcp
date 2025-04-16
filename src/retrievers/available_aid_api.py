import requests
from typing import Optional
from ..retrievers.base import BaseRetriever


class AvailableAidRetriever(BaseRetriever):
    def retrieve(self, query: str, metadata: Optional[dict] = None) -> str:
        student_id = metadata.get("student_id") if metadata else None

        if not student_id:
            return "[AvailableAid API] No student_id provided"

        return f"[AvailableAid API] {student_id} {query}"

        url = f"https://your-api.com/availableFinancialAid?student_id={student_id}"
        try:
            response = requests.get(url)
            return f"[AvailableAid API] {response.text}"
        except Exception as e:
            return f"[AvailableAid API Error] {e}"
