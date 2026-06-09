"""
Single OpenAI-compatible LLM client driven entirely by environment variables.

Local development (LM Studio):
    OPENAI_BASE_URL=http://localhost:1234/v1
    OPENAI_API_KEY=lm-studio          (any non-empty string)
    OPENAI_MODEL=google/gemma-2-2b-it

Production (OpenAI), same code, different env:
    OPENAI_BASE_URL unset (defaults to OpenAI)
    OPENAI_API_KEY=sk-...
    OPENAI_MODEL=gpt-4o-mini

No provider-specific code lives in the agents; they call get_llm() and
generate_text() only.
"""
import os

from langchain_openai import ChatOpenAI


class LLMUnavailable(Exception):
    """Raised when the language model cannot be reached or returns an error."""


def get_llm(temperature: float = 0.2, streaming: bool = False) -> ChatOpenAI:
    return ChatOpenAI(
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        api_key=os.getenv("OPENAI_API_KEY") or "not-needed",
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=temperature,
        timeout=float(os.getenv("LLM_TIMEOUT", "30")),
        max_retries=0,
        streaming=streaming,
    )


def generate_text(system: str, user: str, temperature: float = 0.2) -> str:
    """
    Single non-streaming completion. Raises LLMUnavailable on any failure so the
    calling agent can fall back to deterministic templates (degraded mode).
    """
    try:
        llm = get_llm(temperature=temperature)
        response = llm.invoke(
            [{"role": "system", "content": system}, {"role": "user", "content": user}]
        )
        return response.content.strip()
    except Exception as exc:  # noqa: BLE001 - intentional single fallback boundary
        raise LLMUnavailable(str(exc)) from exc


def stream_text(system: str, user: str, temperature: float = 0.3):
    """
    Token-by-token generator for the education agent / chat sidebar.
    Raises LLMUnavailable if streaming cannot start.
    """
    try:
        llm = get_llm(temperature=temperature, streaming=True)
        for chunk in llm.stream(
            [{"role": "system", "content": system}, {"role": "user", "content": user}]
        ):
            if chunk.content:
                yield chunk.content
    except Exception as exc:  # noqa: BLE001
        raise LLMUnavailable(str(exc)) from exc
