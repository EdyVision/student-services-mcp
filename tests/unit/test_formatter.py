import pytest
from src.formatter import MCPFormatter

sample_contexts = [
    {"content": "This is document one."},
    {"content": "This is document two."},
]


def test_default_prompt_format():
    formatter = MCPFormatter(model_type="default")
    prompt = formatter.format("What is this?", sample_contexts)

    assert "This is document one." in prompt
    assert "What is this?" in prompt
    assert "Answer:" in prompt


def test_phi4_prompt_format():
    formatter = MCPFormatter(model_type="phi-4")
    prompt = formatter.format("Explain financial aid.", sample_contexts)

    assert "You are an assistant trained to help students" in prompt
    assert "- This is document one." in prompt
