import type {
  WaterTestResult,
  CommunityRiskData,
  ScenarioId,
  ParameterReading,
  RiskLevel,
} from "@/types";
import {
  scenarioResults,
  scenarioReplies,
  communityRisk,
} from "./mock-data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Analyze an uploaded water sample.
 *
 * Backend contract (Member 3 / Member 4 orchestration):
 *   POST {API_URL}/api/analyze
 *   body: multipart/form-data { water_image, test_strip_image?, area_id? }
 *   returns: WaterTestResult
 */
export async function analyzeWaterTest(
  waterImage: File,
  testStripImage?: File,
  areaId?: string
): Promise<WaterTestResult> {
  // TODO: wire to backend
  // const formData = new FormData();
  // formData.append("water_image", waterImage);
  // if (testStripImage) formData.append("test_strip_image", testStripImage);
  // if (areaId) formData.append("area_id", areaId);
  // const res = await fetch(`${API_URL}/api/analyze`, { method: "POST", body: formData });
  // return res.json();
  void waterImage;
  void testStripImage;
  void areaId;
  await new Promise((r) => setTimeout(r, 400));
  return { ...scenarioResults.microbial, timestamp: new Date().toISOString() };
}

/**
 * Analyze a manually entered set of parameter readings.
 *
 * Backend contract:
 *   POST {API_URL}/api/analyze/manual
 *   body: { parameters: Record<string, number>, area_id? }
 *   returns: WaterTestResult
 *
 * Param keys: ph, chlorine_residual_ppm, turbidity_ntu, nitrate_ppm,
 * nitrite_ppm, hardness_ppm, iron_ppm
 */
export async function analyzeManualTest(
  params: Record<string, number>,
  areaId?: string
): Promise<WaterTestResult> {
  // TODO: wire to backend
  void areaId;
  await new Promise((r) => setTimeout(r, 400));
  return buildManualResult(params);
}

/**
 * Run a preset demo scenario (used by the live demo controls).
 *
 * Backend contract:
 *   POST {API_URL}/api/scenario
 *   body: { scenario, area_id? }
 *   returns: WaterTestResult
 */
export async function runScenario(
  scenario: ScenarioId,
  areaId?: string
): Promise<WaterTestResult> {
  // TODO: wire to backend
  void areaId;
  await new Promise((r) => setTimeout(r, 300));
  return { ...scenarioResults[scenario], timestamp: new Date().toISOString() };
}

/**
 * Ask the master agent a question about the current result.
 *
 * Backend contract:
 *   POST {API_URL}/api/chat
 *   body: { message, result_id?, scenario? }
 *   returns: { reply: string }   (streaming can be added later)
 */
export async function sendChatMessage(
  message: string,
  scenario?: ScenarioId
): Promise<string> {
  // TODO: wire to backend (streaming)
  void message;
  await new Promise((r) => setTimeout(r, 700));
  if (scenario) return scenarioReplies[scenario];
  return "Run a demo scenario or upload a sample and I'll explain the results and the safest next steps for your situation.";
}

/**
 * Fetch community risk data for a selected area.
 *
 * Backend contract:
 *   GET {API_URL}/api/community/{area_id}
 *   returns: CommunityRiskData
 */
export async function getCommunityRisk(
  areaId: string
): Promise<CommunityRiskData> {
  // TODO: wire to backend
  await new Promise((r) => setTimeout(r, 350));
  return communityRisk[areaId];
}

/* ----------------------------- mock helpers ----------------------------- */

interface ParamSpec {
  key: string;
  name: string;
  unit: string;
  /** [cautionAbove, unsafeAbove] thresholds; pH handled specially */
  caution: number;
  unsafe: number;
  max: number;
}

const PARAM_SPECS: ParamSpec[] = [
  { key: "ph", name: "pH", unit: "", caution: 0, unsafe: 0, max: 14 },
  { key: "chlorine_residual_ppm", name: "Chlorine", unit: "mg/L", caution: 2, unsafe: 4, max: 5 },
  { key: "turbidity_ntu", name: "Turbidity", unit: "NTU", caution: 5, unsafe: 10, max: 20 },
  { key: "nitrate_ppm", name: "Nitrate", unit: "mg/L", caution: 25, unsafe: 50, max: 80 },
  { key: "nitrite_ppm", name: "Nitrite", unit: "mg/L", caution: 1, unsafe: 3, max: 5 },
  { key: "hardness_ppm", name: "Hardness", unit: "mg/L", caution: 200, unsafe: 400, max: 500 },
  { key: "iron_ppm", name: "Iron", unit: "mg/L", caution: 0.3, unsafe: 1, max: 3 },
];

function classify(spec: ParamSpec, value: number): RiskLevel {
  if (spec.key === "ph") {
    if (value < 5.5 || value > 9) return "unsafe";
    if (value < 6.5 || value > 8.5) return "caution";
    return "safe";
  }
  if (value >= spec.unsafe) return "unsafe";
  if (value >= spec.caution) return "caution";
  return "safe";
}

function buildManualResult(params: Record<string, number>): WaterTestResult {
  const parameters: ParameterReading[] = PARAM_SPECS.filter(
    (s) => params[s.key] !== undefined && !Number.isNaN(params[s.key])
  ).map((s) => {
    const value = params[s.key];
    const riskLevel = classify(s, value);
    const scale =
      s.key === "ph"
        ? Math.min(1, Math.abs(value - 7) / 4)
        : Math.min(1, value / s.max);
    return { name: s.name, value, unit: s.unit, riskLevel, scale };
  });

  const order: Record<RiskLevel, number> = {
    safe: 0,
    caution: 1,
    unsafe: 2,
    unknown: 0,
  };
  const overallRisk = parameters.reduce<RiskLevel>(
    (worst, p) => (order[p.riskLevel] > order[worst] ? p.riskLevel : worst),
    "safe"
  );

  const summaries: Record<RiskLevel, string> = {
    safe: "All entered readings fall within safe drinking ranges.",
    caution:
      "Some readings are outside the ideal range. Treatment is recommended before drinking.",
    unsafe:
      "One or more readings are in the unsafe range. Do not drink without proper treatment or testing.",
    unknown: "Unable to determine an overall risk from the entered readings.",
  };

  const recsByRisk: Record<RiskLevel, string[]> = {
    safe: [
      "Water appears suitable for drinking based on these readings.",
      "Store in a clean covered container.",
      "Re-test after heavy rain or supply changes.",
    ],
    caution: [
      "Let visible particles settle before treatment.",
      "Filter through a clean cloth or household filter.",
      "Boil for at least 1 minute if microbial contamination is suspected.",
      "Store treated water in a clean covered container.",
    ],
    unsafe: [
      "Do not drink this water based on these readings.",
      "If chemical contamination is suspected, do not rely on boiling.",
      "Use an alternative source if available.",
      "Seek proper laboratory testing.",
    ],
    unknown: ["Enter parameter readings to receive guidance."],
  };

  return {
    id: `manual-${Date.now()}`,
    timestamp: new Date().toISOString(),
    scenario: "microbial",
    scenarioLabel: "Manual entry",
    waterAppearance: "clear",
    overallRisk,
    confidence: 0.9,
    summary: summaries[overallRisk],
    parameters,
    recommendations: recsByRisk[overallRisk],
    warnings:
      overallRisk === "unsafe"
        ? [
            "Readings indicate unsafe water. If chemical contamination is suspected (very low pH, high nitrate), boiling will not make it safe.",
          ]
        : [],
    sources: [
      "WHO Guidelines for Drinking-water Quality (4th edition)",
      "CDC Safe Water System",
    ],
  };
}
