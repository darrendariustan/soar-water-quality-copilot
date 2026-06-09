"""
Education Agent.

Explains the diagnosis and treatment in simple language. Uses the LLM when
available and falls back to a deterministic template (degraded mode) when the
model cannot be reached. A streaming generator is exposed for the chat sidebar
(st.write_stream / SSE), wired by the backend team.
"""
from agents.llm import generate_text, stream_text, LLMUnavailable
from agents.state import GraphState

_SYSTEM = (
    "You are a water safety educator for communities with limited lab access.\n"
    "Plan-Execute-Reflect instructions:\n"
    "- PLAN: Review the provided context (risk level, parameters, and recommended steps).\n"
    "- EXECUTE: Explain the diagnosis and practical treatment steps clearly in plain language. "
    "Keep it to a maximum of 4 short, actionable sentences. No emojis.\n"
    "- REFLECT: Ensure you do not contradict the provided assessment or treatment steps. "
    "Do NOT include any defensive filler text, caveats, or generic AI disclaimers."
)


def _context(state: GraphState) -> str:
    quality = state["quality"]
    treatment = state.get("treatment")
    steps = "; ".join(treatment.steps) if treatment else ""
    return (
        f"Water appearance: {state['cv'].water_appearance}. "
        f"Overall risk: {quality.overall_risk}. "
        f"Concerns: {', '.join(quality.failed_parameters) or 'none'}. "
        f"Recommended steps: {steps}."
    )


def _fallback(state: GraphState) -> str:
    quality = state["quality"]
    if quality.overall_risk == "safe":
        return (
            "Your water passed this first-level screen. This is not a lab test, "
            "so keep storing it clean and re-test if it changes."
        )
    return (
        f"This screen flagged {quality.overall_risk} water "
        f"({', '.join(quality.failed_parameters) or 'see readings'}). "
        "Follow the recommended steps and seek proper testing if you can."
    )


def education_agent(state: GraphState) -> dict:
    try:
        text = generate_text(_SYSTEM, _context(state), temperature=0.3)
        return {"education": text}
    except LLMUnavailable as exc:
        warnings = list(state.get("warnings", []))
        warnings.append("Education explanation generated locally (LLM unavailable).")
        return {
            "education": _fallback(state),
            "warnings": warnings,
            "degraded": True,
            "degraded_capabilities": list(state.get("degraded_capabilities", [])) + ["llm"],
        }


def stream_education(state: GraphState):
    """Token-by-token generator for the chat sidebar; falls back to one chunk."""
    try:
        yield from stream_text(_SYSTEM, _context(state), temperature=0.3)
    except LLMUnavailable:
        yield _fallback(state)
