"""
Loads the cited water-safety knowledge base and provides deterministic
parameter classification and guidance lookup.

The JSON files in this package are the seed source of truth. Every threshold
and rule carries a source_id that resolves to an authoritative reference in
sources.json (WHO, EPA, CDC, USGS). The Exa web crawl agent can later extend
this same knowledge base with fresh guidance.
"""
import json
import functools
from pathlib import Path

_DIR = Path(__file__).parent

# Risk ordering used to cap aesthetic parameters and to aggregate overall risk.
RISK_ORDER = {"safe": 0, "caution": 1, "unsafe": 2, "unknown": 3}


def _load(name: str) -> dict | list:
    with open(_DIR / name, encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=1)
def thresholds() -> dict:
    return _load("thresholds.json")


@functools.lru_cache(maxsize=1)
def safety_rules() -> list:
    return _load("safety_rules.json")


@functools.lru_cache(maxsize=1)
def guidance() -> dict:
    return _load("guidance.json")


@functools.lru_cache(maxsize=1)
def sources() -> dict:
    return _load("sources.json")


def source_citation(source_id: str) -> str:
    """Return a short 'Org, Title' citation string for a source id."""
    src = sources().get(source_id)
    if not src:
        return source_id
    return f"{src['organisation']}: {src['title']}"


def _cap(risk: str, max_risk: str) -> str:
    if RISK_ORDER[risk] > RISK_ORDER[max_risk]:
        return max_risk
    return risk


def classify_parameter(key: str, value: float) -> dict | None:
    """
    Classify a single reading against the cited thresholds.

    Returns a dict with label, unit, value, risk_level, scale (0-1 for UI bars),
    and the source citation, or None if the parameter is not in the knowledge base.
    """
    spec = thresholds().get(key)
    if spec is None or value is None:
        return None

    if spec["safe_min"] <= value <= spec["safe_max"]:
        risk = "safe"
    elif spec["caution_min"] <= value <= spec["caution_max"]:
        risk = "caution"
    else:
        risk = "unsafe"
    risk = _cap(risk, spec.get("max_risk", "unsafe"))

    scale = max(0.0, min(1.0, value / spec["scale_max"])) if spec["scale_max"] else 0.0

    return {
        "key": key,
        "label": spec["label"],
        "unit": spec["unit"],
        "value": value,
        "risk_level": risk,
        "scale": round(scale, 3),
        "source": source_citation(spec["source_id"]),
        "note": spec["note"],
    }


def lookup_guidance(contamination_type: str) -> dict:
    """Return the guidance entry for a contamination type, falling back to safe."""
    g = guidance()
    return g.get(contamination_type, g["safe"])


def guidance_sources(entry: dict) -> list[str]:
    return [source_citation(sid) for sid in entry.get("source_ids", [])]
