"""
Computer Vision Agent.

The CV model (Amazon Rekognition, owned by a teammate via tools/cv_tool.py) runs
upstream and populates the request appearance + test strip payloads. This node
evaluates image quality and confidence, maps water appearance, and flags
low-confidence readings for manual entry. It does not re-run Rekognition because
the request carries readings, not image bytes.
"""
from agents.schemas import CVAssessment
from agents.state import GraphState

CONFIDENCE_THRESHOLD = 0.6

_APPEARANCE_MAP = {
    "clear": "clear",
    "cloudy": "cloudy",
    "colored": "colored",
    "coloured": "colored",
}

_STRIP_PARAMS = [
    "ph",
    "chlorine_residual_ppm",
    "turbidity_ntu",
    "nitrate_ppm",
    "nitrite_ppm",
    "hardness_ppm",
    "iron_ppm",
]


def cv_agent(state: GraphState) -> dict:
    request = state["request"]
    appearance = request.appearance
    strip = request.test_strip

    water_appearance = _APPEARANCE_MAP.get(
        (appearance.clarity_classification or "clear").lower(), "clear"
    )
    if appearance.particle_detected:
        water_appearance = "contaminated"

    notes: list[str] = []
    low_conf: list[str] = []

    # A single strip confidence governs the readings from that strip.
    if strip.confidence_score < CONFIDENCE_THRESHOLD:
        for key in _STRIP_PARAMS:
            if getattr(strip, key) is not None:
                low_conf.append(key)
        notes.append(
            f"Test strip confidence {strip.confidence_score:.2f} is below "
            f"{CONFIDENCE_THRESHOLD:.2f}; readings flagged for manual confirmation."
        )

    needs_manual = strip.confidence_score < CONFIDENCE_THRESHOLD

    cv = CVAssessment(
        water_appearance=water_appearance,
        appearance_confidence=appearance.confidence_score,
        strip_confidence=strip.confidence_score,
        low_confidence_parameters=low_conf,
        needs_manual_entry=needs_manual,
        notes=notes,
    )
    return {"cv": cv}
