"""Shared LangGraph state passed between every node (hub-and-spoke)."""
from typing import Optional, TypedDict

from schemas import WaterQualityAnalysisRequest
from agents.schemas import (
    CVAssessment,
    CommunityReport,
    ExaResult,
    KnowledgeResult,
    QualityAssessment,
    SafetyReview,
    TreatmentGuidance,
    WaterTestResult,
)


class GraphState(TypedDict, total=False):
    # Input
    request: WaterQualityAnalysisRequest
    scenario: str
    scenario_label: str
    manual_overrides: dict  # parameter key -> operator-supplied value

    # Per-agent outputs written into the hub state
    cv: CVAssessment
    quality: QualityAssessment
    knowledge: KnowledgeResult
    exa: ExaResult
    treatment: TreatmentGuidance
    safety: SafetyReview
    community: CommunityReport
    education: str

    # Final compiled output
    result: WaterTestResult

    # Failure handling / degraded mode
    warnings: list[str]
    degraded: bool
    degraded_capabilities: list[str]
