# from typing import List, Dict, Optional
# import time
#
# from ..core.retrieval_engine import RetrievalEngine
# # from ..apis.bedrock import BedrockLLM
# # from ..apis.huggingface import HuggingFaceLLM
# # from ..apis.local_llm import LocalLLM
# from ..core.rag_formatter import format_prompt, format_response
#
#
# class MultiAPIQueryHandler:
#     def __init__(self, config: Optional[Dict] = None):
#         self.retriever = RetrievalEngine()
#         self.model_backends = {
#             "bedrock": BedrockLLM(),
#             "huggingface": HuggingFaceLLM(),
#             "local": LocalLLM(),
#         }
#
#     def query(
#         self,
#         user_input: str,
#         context_priority: List[str],
#         model_backend: str = "bedrock",
#         metadata: Optional[Dict] = None,
#         mode: str = "insights",
#     ) -> Dict:
#         # === Step 1: Retrieve context ===
#         context_blob, context_sources = self.retriever.retrieve(
#             user_input, context_priority
#         )
#
#         # === Step 2: Format prompt ===
#         prompt = format_prompt(user_input, context_blob, mode=mode)
#
#         # === Step 3: Dispatch to model ===
#         model = self.model_backends.get(model_backend)
#         if not model:
#             raise ValueError(f"Unknown model backend: {model_backend}")
#
#         start = time.time()
#         response = model.generate(prompt)
#         end = time.time()
#
#         # === Step 4: Format output ===
#         return format_response(
#             user_input=user_input,
#             context_sources=context_sources,
#             context_tokens=len(context_blob.split()),
#             model_backend=model_backend,
#             output=response.get("text"),
#             generation_tokens=response.get("tokens", 0),
#             latency=end - start,
#         )
