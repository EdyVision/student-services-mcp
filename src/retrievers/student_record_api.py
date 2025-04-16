import requests
from typing import Optional
from ..retrievers.base import BaseRetriever


class StudentRecordRetriever(BaseRetriever):
    def retrieve(self, query: str, metadata: Optional[dict] = None) -> str:
        student_id = metadata.get("student_id")
        if not student_id:
            return "[StudentRecord API] No student_id provided"

        url = f"https://your-api.com/studentRecord?student_id={student_id}"
        try:
            response = requests.get(url)
            return f"[StudentRecord API] {response.text}"
        except Exception as e:
            return f"[StudentRecord API Error] {e}"
