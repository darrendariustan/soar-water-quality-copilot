"""
Water Quality Interpretation Agent.

Deterministically maps test strip readings to risk categories using the cited
threshold knowledge base (WHO/EPA/CDC/USGS). No LLM is involved here so the
classification is reproducible and traceable to sources. Operator overrides in
state replace the CV-derived value for a parameter.
"""
from knowledge.loader import classify_parameter, RISK_ORDER
from agents.schemas import ParameterReading, QualityAssessment
from agents.state import GraphState

_STRIP_PARAMS = [
    "ph",
    "chlorine_residual_ppm",
    "turbidity_ntu",
    "nitrate_ppm",
    "nitrite_ppm",
    "hardness_ppm",
    "iron_ppm",
]


def _worst(risks: list[str]) -> str:
    if not risks:
        return "unknown"
    return max(risks, key=lambda r: RISK_ORDER.get(r, 0))


def _contamination_type(by_key: dict, appearance: str) -> str:
    def risk(key):
        return by_key[key]["risk_level"] if key in by_key else "safe"

    chemical = risk("nitrate_ppm") in ("caution", "unsafe") or risk("nitrite_ppm") in (
        "caution",
        "unsafe",
    )
    microbial = (
        risk("turbidity_ntu") == "unsafe"
        or appearance in ("cloudy", "contaminated")
        or risk("chlorine_residual_ppm") == "caution"
    )
    turbid = risk("turbidity_ntu") == "caution"
    aesthetic = risk("hardness_ppm") == "caution" or risk("iron_ppm") == "caution"

    if chemical:
        return "nitrate"
    if microbial:
        return "microbial"
    if turbid:
        return "turbidity"
    if aesthetic:
        return "aesthetic"
    return "none"


def water_quality_agent(state: GraphState) -> dict:
    strip = state["request"].test_strip
    overrides = state.get("manual_overrides", {}) or {}
    appearance = state["cv"].water_appearance

    readings: list[ParameterReading] = []
    by_key: dict = {}
    failed: list[str] = []
    sources: set[str] = set()

    for key in _STRIP_PARAMS:
        value = overrides.get(key, getattr(strip, key))
        classified = classify_parameter(key, value)
        if classified is None:
            continue
        by_key[key] = classified
        sources.add(classified["source"])
        readings.append(
            ParameterReading(
                name=classified["label"],
                value=classified["value"],
                unit=classified["unit"],
                riskLevel=classified["risk_level"],
                scale=classified["scale"],
            )
        )
        if classified["risk_level"] in ("caution", "unsafe"):
            failed.append(classified["label"])

    overall = _worst([r.riskLevel for r in readings])
    contamination = _contamination_type(by_key, appearance)

    assessment = QualityAssessment(
        parameters=readings,
        overall_risk=overall,
        contamination_type=contamination,
        failed_parameters=failed,
        sources=sorted(sources),
    )
    return {"quality": assessment}
