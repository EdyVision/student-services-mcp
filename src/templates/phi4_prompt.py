def build_phi4_prompt(query: str, contexts: list[dict]) -> str:
    context_str = "\n\n".join([f"- {c['content']}" for c in contexts])
    return f"""You are an assistant trained to help students with financial aid.

            Here is some information to help:
            
            {context_str}
            
            Student asked:
            {query}
            
            Respond clearly and helpfully:"""
