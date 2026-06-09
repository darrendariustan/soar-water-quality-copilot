"""
Treatment Guidance Agent.

Builds practical household treatment steps from the retrieved cited guidance.
Steps are taken from the knowledge base (deterministic and source-backed) rather
than invented by the model. The output is then gated by the safety agent before
being finalised.
"""
from agents.schemas import TreatmentGuidance
from agents.state import GraphState


def treatment_guidance_agent(state: GraphState) -> dict:
    knowledge = state["knowledge"]
    exa = state.get("exa")

    sources = list(knowledge.sources)
    if exa and exa.used_live:
        for s in exa.sources:
            sources.append(f"{s.title} ({s.url})")

    guidance = TreatmentGuidance(
        steps=list(knowledge.steps),
        sources=sources,
    )
    return {"treatment": guidance}
