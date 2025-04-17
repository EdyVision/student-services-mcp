def build_default_prompt(query: str, contexts: list[dict]) -> str:
    context_str = "\n\n".join([c["content"] for c in contexts])
    return f"""Answer the following question using the context below.
            Context:
            {context_str}
            
            Question: {query}
            Answer:"""
