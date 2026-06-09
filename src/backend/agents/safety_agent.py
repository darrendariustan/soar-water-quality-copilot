"""
Safety and Compliance Agent.

Applies deterministic hard-gate rules from the cited safety_rules knowledge base
(not the LLM). It inspects the proposed treatment steps and the assessed
contamination, blocks hazardous actions (for example boiling chemically
contaminated water), and attaches source-backed warnings. This runs after the
treatment agent and before the guidance is finalised.
"""
from knowledge.loader import safety_rules, source_citation
from agents.schemas import SafetyReview
from agents.state import GraphState

# Maps the water-quality contamination_type to the tags used by safety rules.
_CONTAMINATION_TAGS = {
    "nitrate": {"chemical"},
    "chemical": {"chemical", "fuel", "pesticide", "industrial", "heavy_metal"},
}


def safety_agent(state: GraphState) -> dict:
    quality = state["quality"]
    treatment = state.get("treatment")
    steps = list(treatment.steps) if treatment else []
    overrides = state.get("manual_overrides", {}) or {}
    turbidity = overrides.get("turbidity_ntu", state["request"].test_strip.turbidity_ntu)

    active_tags = _CONTAMINATION_TAGS.get(quality.contamination_type, set())

    blocked_actions: list[str] = []
    warnings: list[str] = []
    triggered: list[str] = []
    approved = True

    for rule in safety_rules():
        matched = False

        if rule.get("triggers_contamination"):
            if active_tags & set(rule["triggers_contamination"]):
                matched = True

        param_trigger = rule.get("triggers_parameter")
        if param_trigger:
            for key, cond in param_trigger.items():
                value = overrides.get(key, getattr(state["request"].test_strip, key, None))
                if value is not None and "above" in cond and value > cond["above"]:
                    matched = True

        if not matched:
            continue

        triggered.append(rule["id"])
        warnings.append(f"{rule['warning']} (Source: {source_citation(rule['source_id'])})")

        for action in rule.get("blocks_actions", []):
            kept = []
            for step in steps:
                low = step.lower()
                # Only block steps that recommend the action, not those warning against it.
                recommends = action in low and not any(
                    neg in low for neg in ("do not", "don't", "avoid", "never", "not ")
                )
                if recommends:
                    blocked_actions.append(step)
                else:
                    kept.append(step)
            steps = kept

        if rule.get("risk_level") == "unsafe":
            approved = False

    review = SafetyReview(
        approved=approved,
        blocked_actions=blocked_actions,
        warnings=warnings,
        triggered_rules=triggered,
    )
    # Write back the (possibly filtered) treatment steps so blocked actions are removed.
    updated_treatment = treatment.model_copy(update={"steps": steps}) if treatment else None
    out = {"safety": review}
    if updated_treatment is not None:
        out["treatment"] = updated_treatment
    return out
