from typing import List, Tuple, Optional
from ..retrievers.available_aid_api import AvailableAidRetriever
from ..retrievers.student_record_api import StudentRecordRetriever
from ..retrievers.faiss import FAISSRetriever
from ..retrievers.dynamodb import DynamoDBRetriever
from ..retrievers.s3 import S3Retriever


class RetrievalEngine:
    def __init__(self):
        self.plugins = {
            "faiss": FAISSRetriever(),
            "dynamodb": DynamoDBRetriever(),
            "s3": S3Retriever(),
            "available_aid_api": AvailableAidRetriever(),
            "student_record_api": StudentRecordRetriever(),
        }

    def retrieve(
        self, query: str, context_priority: List[str], metadata: Optional[dict] = None
    ) -> Tuple[str, List[str]]:
        context_chunks = []
        sources_used = []

        for source in context_priority:
            retriever = self.plugins.get(source)
            if retriever:
                try:
                    result = retriever.retrieve(query, metadata)
                    context_chunks.append(result)
                    sources_used.append(source)
                except Exception as e:
                    print(f"[WARN] Failed to retrieve from {source}: {e}")

        combined_context = "\n".join(context_chunks)
        return combined_context, sources_used
