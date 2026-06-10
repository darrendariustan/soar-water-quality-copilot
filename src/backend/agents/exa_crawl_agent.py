"""
Exa Web Crawl Agent.

Invoked by the master agent only when stored knowledge is insufficient for the
contaminant or region. Builds a targeted query for trusted public sources and
calls the Exa tool, which degrades gracefully when no API key is present.
"""
from tools.exa_crawl_tool import search_trusted
from agents.schemas import ExaResult, ExaSource
from agents.state import GraphState


def exa_crawl_agent(state: GraphState) -> dict:
    quality = state["quality"]
    request = state["request"]
    region = request.location or "general"

    query = (
        f"safe drinking water guidance for {quality.contamination_type} contamination "
        f"in {region}; household treatment and warnings"
    )

    found = search_trusted(query)
    exa = ExaResult(
        used_live=found["used_live"],
        sources=[ExaSource(**s) for s in found["sources"]],
        note=found["note"],
    )
    
    out = {"exa": exa}
    if not found["used_live"] and found["note"]:
        warnings = list(state.get("warnings", []))
        warnings.append(found["note"])
        out["warnings"] = warnings
        out["degraded"] = True
        degraded_caps = list(state.get("degraded_capabilities", []))
        if "exa" not in degraded_caps:
            degraded_caps.append("exa")
        out["degraded_capabilities"] = degraded_caps

    return out
