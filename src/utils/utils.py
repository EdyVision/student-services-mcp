from transformers import AutoTokenizer


def truncate_contexts(
    contexts: list[dict], model_name: str, max_tokens: int
) -> list[dict]:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    token_count = 0
    result = []

    for c in contexts:
        tokens = tokenizer.encode(c["content"], add_special_tokens=False)
        if token_count + len(tokens) > max_tokens:
            break
        result.append(c)
        token_count += len(tokens)

    return result
