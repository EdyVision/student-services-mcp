from typing import List, Dict
import time


def format_prompt(user_input: str, context: str, mode: str = "insights") -> str:
    if mode == "insights":
        return f"""Analyze the following question using the context provided. Be concise, fact-based, and structured."""

    return f"""
        You are a helpful assistant. Use the following context to answer the question:
        
        Context:
        {context}
        
        Question:
        {user_input}
        
        Answer:
        """


def format_response(
    user_input: str,
    context_sources: List[str],
    context_tokens: int,
    model_backend: str,
    output: str,
    generation_tokens: int,
    latency: float,
) -> Dict:
    return {
        "query": user_input,
        "response": output,
        "model_used": model_backend,
        "retrieval_sources": context_sources,
        "context_tokens": context_tokens,
        "generation_tokens": generation_tokens,
        "latency_ms": int(latency * 1000),
    }
