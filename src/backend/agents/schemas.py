"""
Pydantic models exchanged between agents and the final output contract.

ParameterReading and WaterTestResult mirror the frontend TypeScript types in
src/frontend/src/types/index.ts so the FastAPI layer can return the master
agent output to the UI without translation.
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field

RiskLevel = Literal["safe", "caution", "unsafe", "unknown"]


class ParameterReading(BaseModel):
    name: str
    value: float
    unit: str = ""
    riskLevel: RiskLevel = "unknown"
    scale: float = Field(0.0, ge=0.0, le=1.0)


class CVAssessment(BaseModel):
    """Output of the CV agent: confidence and quality evaluation of CV readings."""
    water_appearance: Literal["clear", "cloudy", "colored", "contaminated"] = "clear"
    appearance_confidence: float = Field(0.0, ge=0.0, le=1.0)
    strip_confidence: float = Field(0.0, ge=0.0, le=1.0)
    low_confidence_parameters: list[str] = Field(default_factory=list)
    needs_manual_entry: bool = False
    notes: list[str] = Field(default_factory=list)


class QualityAssessment(BaseModel):
    """Output of the water quality interpretation agent."""
    parameters: list[ParameterReading] = Field(default_factory=list)
    overall_risk: RiskLevel = "unknown"
    contamination_type: str = "none"
    failed_parameters: list[str] = Field(default_factory=list)
    unsupported_parameters: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class KnowledgeResult(BaseModel):
    """Output of the AWS knowledge retrieval agent."""
    title: str = ""
    summary: str = ""
    steps: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    sufficient: bool = False


class ExaSource(BaseModel):
    title: str
    url: str
    summary: str = ""


class ExaResult(BaseModel):
    """Output of the Exa web crawl agent."""
    used_live: bool = False
    sources: list[ExaSource] = Field(default_factory=list)
    note: str = ""


class TreatmentGuidance(BaseModel):
    """Output of the treatment guidance agent."""
    steps: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class SafetyReview(BaseModel):
    """Output of the safety and compliance agent."""
    approved: bool = True
    blocked_actions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    triggered_rules: list[str] = Field(default_factory=list)


class CommunityReport(BaseModel):
    """Output of the community reporting agent (alert held pending review)."""
    area: Optional[str] = None
    anonymised_user_id: str = ""
    overall_risk: RiskLevel = "unknown"
    failed_parameters: list[str] = Field(default_factory=list)
    alert_status: Literal["pending_review", "none"] = "none"
    escalation: str = ""


class WaterTestResult(BaseModel):
    """Final user-facing result. Mirrors the frontend WaterTestResult type."""
    id: str
    timestamp: str
    scenario: str = "custom"
    scenarioLabel: str = ""
    waterAppearance: Literal["clear", "cloudy", "colored", "contaminated"] = "clear"
    overallRisk: RiskLevel = "unknown"
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    summary: str = ""
    parameters: list[ParameterReading] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    exaContexts: list[dict] = Field(default_factory=list)
