export type RiskLevel = "safe" | "caution" | "unsafe" | "unknown";

export type ScenarioId = "safe" | "microbial" | "chemical";

export interface ParameterReading {
  name: string;
  value: number;
  unit: string;
  riskLevel: RiskLevel;
  /** Normalized 0-1 position on the parameter's safe-to-danger scale, for bars */
  scale: number;
}

export interface WaterTestResult {
  id: string;
  timestamp: string;
  scenario: ScenarioId;
  scenarioLabel: string;
  waterAppearance: "clear" | "cloudy" | "colored" | "contaminated";
  overallRisk: RiskLevel;
  confidence: number;
  summary: string;
  parameters: ParameterReading[];
  recommendations: string[];
  warnings: string[];
  sources: string[];
  exaContexts?: { title: string; url: string; summary: string }[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface CommunityArea {
  id: string;
  name: string;
  region: string;
}

export interface CommunityRiskData {
  areaId: string;
  unsafeReadings: number;
  totalReadings: number;
  commonFailures: string[];
  trend: "improving" | "stable" | "worsening";
  escalation: string;
  lastUpdated: string;
  history: TrendPoint[];
  parameterFailures: ParameterFailure[];
}

export interface TrendPoint {
  month: string;
  unsafe: number;
  safe: number;
}

export interface ParameterFailure {
  parameter: string;
  failures: number;
}

export interface AgentNode {
  id: string;
  name: string;
  description: string;
}
