"""
Master Water Safety Agent and LangGraph orchestration.

Hub-and-spoke topology: the master builds the graph, owns the conditional
routing (the Exa web crawl runs only when stored knowledge is insufficient), and
compiles the final user-facing WaterTestResult from the spoke outputs in state.

Public entrypoint: run_pipeline(request) -> WaterTestResult.
"""
import uuid
from datetime import datetime, timezone

from langgraph.graph import StateGraph, START, END

from schemas import WaterQualityAnalysisRequest
from agents.state import GraphState
from agents.schemas import WaterTestResult
from agents.cv_agent import cv_agent
from agents.water_quality_agent import water_quality_agent
from agents.aws_retrieval_agent import aws_retrieval_agent
from agents.exa_crawl_agent import exa_crawl_agent
from agents.treatment_guidance_agent import treatment_guidance_agent
from agents.safety_agent import safety_agent
from agents.community_reporting_agent import community_reporting_agent
from agents.education_agent import education_agent


def _route_after_retrieval(state: GraphState) -> str:
    """Master routing decision: crawl the web only when stored knowledge is thin."""
    return "treatment" if state["knowledge"].sufficient else "exa_crawl"


def _summary(state: GraphState) -> str:
    quality = state["quality"]
    failed = ", ".join(quality.failed_parameters)
    if quality.overall_risk == "safe":
        return "All screened parameters are within safe ranges. This is a first-level screen, not a laboratory test."
    if quality.overall_risk == "caution":
        return f"Some readings need caution ({failed}). Follow the recommended steps below."
    if quality.overall_risk == "unsafe":
        return f"Unsafe water detected ({failed}). Follow the warnings and steps below before any use."
    return "Water quality could not be fully determined. Confirm the readings."


def master_agent(state: GraphState) -> dict:
    """Final node: compile the user-facing result from all spoke outputs."""
    quality = state["quality"]
    cv = state["cv"]
    treatment = state.get("treatment")
    safety = state.get("safety")
    knowledge = state["knowledge"]

    overall = quality.overall_risk
    if safety and not safety.approved:
        overall = "unsafe"

    recommendations = list(treatment.steps) if treatment else []
    if not recommendations:
        recommendations = ["Use a different, known-safe water source and seek proper testing."]

    warnings = list(state.get("warnings", []))
    if safety:
        warnings = safety.warnings + warnings

    sources: list[str] = []
    for s in quality.sources + (treatment.sources if treatment else []) + knowledge.sources:
        if s not in sources:
            sources.append(s)

    result = WaterTestResult(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        scenario=state.get("scenario", "custom"),
        scenarioLabel=state.get("scenario_label", "Water sample analysis"),
        waterAppearance=cv.water_appearance,
        overallRisk=overall,
        confidence=round(min(cv.appearance_confidence, cv.strip_confidence), 3),
        summary=_summary(state),
        parameters=quality.parameters,
        recommendations=recommendations,
        warnings=warnings,
        sources=sources,
    )
    return {"result": result}


def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("cv", cv_agent)
    graph.add_node("water_quality", water_quality_agent)
    graph.add_node("aws_retrieval", aws_retrieval_agent)
    graph.add_node("exa_crawl", exa_crawl_agent)
    graph.add_node("treatment", treatment_guidance_agent)
    graph.add_node("safety", safety_agent)
    graph.add_node("education", education_agent)
    graph.add_node("community", community_reporting_agent)
    graph.add_node("master", master_agent)

    graph.add_edge(START, "cv")
    graph.add_edge("cv", "water_quality")
    graph.add_edge("water_quality", "aws_retrieval")
    graph.add_conditional_edges(
        "aws_retrieval", _route_after_retrieval, {"exa_crawl": "exa_crawl", "treatment": "treatment"}
    )
    graph.add_edge("exa_crawl", "treatment")
    graph.add_edge("treatment", "safety")
    graph.add_edge("safety", "education")
    graph.add_edge("education", "community")
    graph.add_edge("community", "master")
    graph.add_edge("master", END)
    return graph.compile()


_COMPILED = None


def get_app():
    global _COMPILED
    if _COMPILED is None:
        _COMPILED = build_graph()
    return _COMPILED


def run_pipeline(
    request: WaterQualityAnalysisRequest,
    scenario: str = "custom",
    scenario_label: str = "Water sample analysis",
    manual_overrides: dict | None = None,
) -> WaterTestResult:
    """Execute the orchestration graph and return the final WaterTestResult."""
    initial: GraphState = {
        "request": request,
        "scenario": scenario,
        "scenario_label": scenario_label,
        "manual_overrides": manual_overrides or {},
        "warnings": [],
        "degraded": False,
        "degraded_capabilities": [],
    }
    final = get_app().invoke(initial)
    return final["result"]
