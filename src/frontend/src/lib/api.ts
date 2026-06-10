import type { WaterTestResult, CommunityRiskData, ScenarioId } from "@/types";
import { scenarioResults, communityRisk } from "./mock-data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Preset parameter sets for the live-demo scenario buttons. These are sent to
// the real backend so the full agent pipeline runs (no CV image required).
const SCENARIO_PARAMS: Record<ScenarioId, Record<string, number>> = {
  safe: {
    ph: 7.2,
    chlorine_residual_ppm: 1.0,
    turbidity_ntu: 0.5,
    nitrate_ppm: 5,
    nitrite_ppm: 0.1,
    hardness_ppm: 120,
    iron_ppm: 0.05,
  },
  microbial: {
    ph: 6.8,
    chlorine_residual_ppm: 0.0,
    turbidity_ntu: 14,
    nitrate_ppm: 18,
    nitrite_ppm: 0.5,
    hardness_ppm: 160,
    iron_ppm: 0.4,
  },
  chemical: {
    ph: 4.3,
    chlorine_residual_ppm: 0.0,
    turbidity_ntu: 9,
    nitrate_ppm: 62,
    nitrite_ppm: 1.5,
    hardness_ppm: 90,
    iron_ppm: 2.4,
  },
};

const SCENARIO_LABELS: Record<ScenarioId, string> = {
  safe: "Safe Water",
  microbial: "Microbiological Outbreak",
  chemical: "Chemical Contamination",
};

async function postSubmission(
  params: Record<string, number>,
  areaId: string | undefined,
  scenario: string,
  scenarioLabel: string
): Promise<WaterTestResult> {
  const res = await fetch(`${API_URL}/cv/submissions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      params,
      area_id: areaId ?? null,
      scenario,
      scenario_label: scenarioLabel,
    }),
  });
  if (!res.ok) throw new Error(`Backend error ${res.status}`);
  return res.json();
}

/**
 * Run a preset demo scenario. Sends preset readings to the agent pipeline.
 * Falls back to local demo data if the backend is unreachable so a live demo
 * never hard-fails on screen.
 */
export async function runScenario(
  scenario: ScenarioId,
  areaId?: string
): Promise<WaterTestResult> {
  try {
    return await postSubmission(
      SCENARIO_PARAMS[scenario],
      areaId,
      scenario,
      SCENARIO_LABELS[scenario]
    );
  } catch (err) {
    console.warn("runScenario fell back to local demo data:", err);
    return { ...scenarioResults[scenario], timestamp: new Date().toISOString() };
  }
}

/** Submit manually entered / operator-adjusted parameters to the agent pipeline. */
export async function analyzeManualTest(
  params: Record<string, number>,
  areaId?: string
): Promise<WaterTestResult> {
  return postSubmission(params, areaId, "custom", "Manual Entry");
}

/** Upload water and (optional) one-to-three test kit photos for CV + agent analysis. */
export async function analyzeWaterTest(
  waterImage: File,
  testStripImages: File[] = [],
  areaId?: string
): Promise<WaterTestResult> {
  const formData = new FormData();
  formData.append("water_image", waterImage);
  for (const img of testStripImages.slice(0, 3)) {
    formData.append("test_strip_images", img);
  }
  if (areaId) formData.append("area_id", areaId);

  const res = await fetch(`${API_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(`Backend error ${res.status}`);
  return res.json();
}

/**
 * Aggregate the chat SSE stream into a single string. The ChatAssistant
 * component streams directly for the live UI; this helper is kept for
 * compatibility and non-streaming callers.
 */
export async function sendChatMessage(
  message: string,
  scenario?: ScenarioId
): Promise<string> {
  const res = await fetch(`${API_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, scenario: scenario ?? null }),
  });
  if (!res.ok || !res.body) throw new Error(`Backend error ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let out = "";
  let done = false;
  while (!done) {
    const { value, done: doneReading } = await reader.read();
    done = doneReading;
    if (value) {
      const chunk = decoder.decode(value, { stream: true });
      for (const line of chunk.split("\n")) {
        if (line.startsWith("data: ")) {
          try {
            const parsed = JSON.parse(line.slice(6));
            if (parsed.text) out += parsed.text;
          } catch {
            // ignore malformed keepalive lines
          }
        }
      }
    }
  }
  return out.replace(/\[UPDATE_PARAMS:.*?\]/, "").trim();
}

/**
 * Community risk data for a selected area. No dedicated backend HTTP route
 * exists yet, so this is served from local demo data.
 */
export async function getCommunityRisk(
  areaId: string
): Promise<CommunityRiskData> {
  await new Promise((r) => setTimeout(r, 200));
  return communityRisk[areaId];
}
