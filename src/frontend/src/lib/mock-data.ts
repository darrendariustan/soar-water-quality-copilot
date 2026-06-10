import type {
  WaterTestResult,
  ChatMessage,
  CommunityArea,
  CommunityRiskData,
  ScenarioId,
  AgentNode,
} from "@/types";

export const agentPipeline: AgentNode[] = [
  { id: "cv", name: "Computer Vision", description: "Reads strip colors and water clarity" },
  { id: "quality", name: "Water Quality", description: "Maps readings to risk categories" },
  { id: "knowledge", name: "Knowledge Retrieval", description: "Searches the AWS safe-water database" },
  { id: "exa", name: "Exa Web Crawl", description: "Fetches trusted public guidance" },
  { id: "treatment", name: "Treatment Guidance", description: "Recommends practical actions" },
  { id: "safety", name: "Safety & Compliance", description: "Blocks unsafe advice" },
  { id: "reporting", name: "Community Reporting", description: "Logs anonymized results" },
];

export const communityAreas: CommunityArea[] = [
  { id: "well-a", name: "Village Well A", region: "Northern District" },
  { id: "river-b", name: "River Collection Point B", region: "Eastern Valley" },
  { id: "tank-c", name: "Rainwater Tank C", region: "Highland Settlement" },
];

export const scenarioResults: Record<ScenarioId, WaterTestResult> = {
  safe: {
    id: "test-safe",
    timestamp: new Date().toISOString(),
    scenario: "safe",
    scenarioLabel: "Safe Water",
    waterAppearance: "clear",
    overallRisk: "safe",
    confidence: 0.94,
    summary:
      "Your water appears clear and all measured parameters fall within safe drinking ranges.",
    parameters: [
      { name: "pH", value: 7.1, unit: "", riskLevel: "safe", scale: 0.2 },
      { name: "Chlorine", value: 0.5, unit: "mg/L", riskLevel: "safe", scale: 0.25 },
      { name: "Turbidity", value: 1.2, unit: "NTU", riskLevel: "safe", scale: 0.15 },
      { name: "Nitrate", value: 6, unit: "mg/L", riskLevel: "safe", scale: 0.2 },
      { name: "Iron", value: 0.1, unit: "mg/L", riskLevel: "safe", scale: 0.1 },
      { name: "Hardness", value: 120, unit: "mg/L", riskLevel: "safe", scale: 0.3 },
    ],
    recommendations: [
      "Water is suitable for drinking based on this screening.",
      "Store in a clean covered container to keep it safe.",
      "Re-test periodically, especially after heavy rain or supply changes.",
    ],
    warnings: [],
    sources: [
      "WHO Guidelines for Drinking-water Quality (4th edition)",
      "CDC Safe Water System",
    ],
  },
  microbial: {
    id: "test-microbial",
    timestamp: new Date().toISOString(),
    scenario: "microbial",
    scenarioLabel: "Microbiological Outbreak",
    waterAppearance: "cloudy",
    overallRisk: "caution",
    confidence: 0.82,
    summary:
      "Your water appears cloudy with elevated turbidity. This suggests possible microbial contamination that treatment can address.",
    parameters: [
      { name: "pH", value: 6.8, unit: "", riskLevel: "safe", scale: 0.3 },
      { name: "Chlorine", value: 0.0, unit: "mg/L", riskLevel: "caution", scale: 0.7 },
      { name: "Turbidity", value: 14.5, unit: "NTU", riskLevel: "unsafe", scale: 0.9 },
      { name: "Nitrate", value: 18, unit: "mg/L", riskLevel: "caution", scale: 0.55 },
      { name: "Iron", value: 0.4, unit: "mg/L", riskLevel: "caution", scale: 0.5 },
      { name: "Hardness", value: 160, unit: "mg/L", riskLevel: "safe", scale: 0.35 },
    ],
    recommendations: [
      "Let visible particles settle before treatment.",
      "Filter the clearer water through a clean cloth or household filter.",
      "Boil the water for at least 1 minute to kill microorganisms.",
      "Store boiled water in a clean covered container.",
    ],
    warnings: [
      "No chlorine residual was detected, so there is no protection against recontamination. Treat before drinking.",
    ],
    sources: [
      "WHO Household Water Treatment and Safe Storage",
      "CDC Making Water Safe in an Emergency",
    ],
  },
  chemical: {
    id: "test-chemical",
    timestamp: new Date().toISOString(),
    scenario: "chemical",
    scenarioLabel: "Chemical Contamination",
    waterAppearance: "colored",
    overallRisk: "unsafe",
    confidence: 0.88,
    summary:
      "Readings indicate possible chemical contamination. Boiling will NOT make this water safe. Do not drink it.",
    parameters: [
      { name: "pH", value: 4.3, unit: "", riskLevel: "unsafe", scale: 0.95 },
      { name: "Chlorine", value: 0.0, unit: "mg/L", riskLevel: "caution", scale: 0.7 },
      { name: "Turbidity", value: 9.0, unit: "NTU", riskLevel: "caution", scale: 0.6 },
      { name: "Nitrate", value: 62, unit: "mg/L", riskLevel: "unsafe", scale: 0.95 },
      { name: "Iron", value: 2.4, unit: "mg/L", riskLevel: "unsafe", scale: 0.9 },
      { name: "Hardness", value: 90, unit: "mg/L", riskLevel: "safe", scale: 0.25 },
    ],
    recommendations: [
      "Do not drink this water and do not rely on boiling.",
      "Use an alternative water source if one is available.",
      "Seek proper laboratory testing before any use.",
      "Report this finding to your local health authority.",
    ],
    warnings: [
      "Suspected chemical contamination (very low pH and high nitrate). Boiling can concentrate some chemicals and will not remove them. Use another source and escalate for testing.",
    ],
    sources: [
      "WHO Chemical Hazards in Drinking-water",
      "EPA Drinking Water Health Advisories",
    ],
  },
};

export const scenarioReplies: Record<ScenarioId, string> = {
  safe: "Good news. All measured parameters are within safe ranges and the water looks clear. Keep it in a clean covered container and re-test after any supply changes.",
  microbial:
    "The cloudiness and high turbidity point to possible microbes. Settle, filter, then boil for at least one minute. Boiling is effective here because the concern is biological.",
  chemical:
    "These readings suggest a chemical problem. Importantly, boiling will not fix chemical contamination and can even concentrate it. Please use another source and seek lab testing.",
};

export const initialChat: ChatMessage[] = [
  {
    id: "msg-1",
    role: "assistant",
    content:
      "Hi, I'm your water safety assistant. Run a demo scenario or upload a sample, then ask me anything about the results or what to do next.",
    timestamp: new Date().toISOString(),
  },
];

export const communityRisk: Record<string, CommunityRiskData> = {
  "well-a": {
    areaId: "well-a",
    unsafeReadings: 3,
    totalReadings: 28,
    commonFailures: ["Turbidity", "Iron"],
    trend: "stable",
    escalation: "Monitor monthly. No escalation needed yet.",
    lastUpdated: "2026-06-08",
    history: [
      { month: "Jan", unsafe: 2, safe: 22 },
      { month: "Feb", unsafe: 3, safe: 19 },
      { month: "Mar", unsafe: 2, safe: 26 },
      { month: "Apr", unsafe: 4, safe: 21 },
      { month: "May", unsafe: 3, safe: 28 },
      { month: "Jun", unsafe: 3, safe: 25 },
    ],
    parameterFailures: [
      { parameter: "Turbidity", failures: 9 },
      { parameter: "Iron", failures: 6 },
      { parameter: "pH", failures: 3 },
    ],
  },
  "river-b": {
    areaId: "river-b",
    unsafeReadings: 7,
    totalReadings: 24,
    commonFailures: ["Turbidity", "Nitrate", "pH"],
    trend: "worsening",
    escalation: "Repeated unsafe readings. Recommend escalation to local health authority.",
    lastUpdated: "2026-06-09",
    history: [
      { month: "Jan", unsafe: 4, safe: 20 },
      { month: "Feb", unsafe: 6, safe: 18 },
      { month: "Mar", unsafe: 5, safe: 19 },
      { month: "Apr", unsafe: 8, safe: 16 },
      { month: "May", unsafe: 7, safe: 17 },
      { month: "Jun", unsafe: 9, safe: 15 },
    ],
    parameterFailures: [
      { parameter: "Turbidity", failures: 14 },
      { parameter: "Nitrate", failures: 11 },
      { parameter: "pH", failures: 8 },
      { parameter: "Iron", failures: 4 },
    ],
  },
  "tank-c": {
    areaId: "tank-c",
    unsafeReadings: 1,
    totalReadings: 19,
    commonFailures: ["pH"],
    trend: "improving",
    escalation: "Conditions improving. Continue routine monitoring.",
    lastUpdated: "2026-06-07",
    history: [
      { month: "Jan", unsafe: 4, safe: 12 },
      { month: "Feb", unsafe: 3, safe: 15 },
      { month: "Mar", unsafe: 3, safe: 16 },
      { month: "Apr", unsafe: 2, safe: 18 },
      { month: "May", unsafe: 2, safe: 17 },
      { month: "Jun", unsafe: 1, safe: 19 },
    ],
    parameterFailures: [
      { parameter: "pH", failures: 5 },
      { parameter: "Turbidity", failures: 2 },
    ],
  },
};
