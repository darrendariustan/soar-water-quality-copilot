"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, Droplets } from "lucide-react";
import type { WaterTestResult, ScenarioId } from "@/types";
import { analyzeWaterTest, runScenario, analyzeManualTest } from "@/lib/api";
import { agentPipeline } from "@/lib/mock-data";
import { LocationSelector } from "@/components/app/LocationSelector";
import { SampleInput } from "@/components/app/SampleInput";
import { AgentOrchestration } from "@/components/app/AgentOrchestration";
import { DiagnosisPanel } from "@/components/app/DiagnosisPanel";
import { CommunityRisk } from "@/components/app/CommunityRisk";
import { ChatAssistant } from "@/components/app/ChatAssistant";

export default function AppPage() {
  const [areaId, setAreaId] = useState<string | null>(null);
  const [result, setResult] = useState<WaterTestResult | null>(null);
  const [running, setRunning] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [activeScenario, setActiveScenario] = useState<ScenarioId | null>(null);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);
  const resultRef = useRef<WaterTestResult | null>(null);

  // Keep ref in sync to avoid stale closures in chat
  useEffect(() => {
    resultRef.current = result;
  }, [result]);

  const runPipeline = async (fetcher: () => Promise<WaterTestResult>) => {
    timers.current.forEach(clearTimeout);
    timers.current = [];
    setResult(null);
    setRunning(true);
    setActiveIndex(0);

    const stepMs = 420;
    agentPipeline.forEach((_, i) => {
      timers.current.push(setTimeout(() => setActiveIndex(i), i * stepMs));
    });

    const data = await fetcher();
    const total = agentPipeline.length * stepMs;
    timers.current.push(
      setTimeout(() => {
        setActiveIndex(agentPipeline.length);
        setRunning(false);
        setResult(data);
      }, total)
    );
  };

  const handleScenario = (scenario: ScenarioId) => {
    setActiveScenario(scenario);
    runPipeline(() => runScenario(scenario, areaId ?? undefined));
  };

  const handleUpload = (waterImage: File, testStripImage?: File) => {
    setActiveScenario(null);
    runPipeline(() =>
      analyzeWaterTest(waterImage, testStripImage, areaId ?? undefined)
    );
  };

  const handleManualSubmit = (params: Record<string, number>) => {
    setActiveScenario(null);
    runPipeline(() => analyzeManualTest(params, areaId ?? undefined));
  };

  const handleChatUpdateParams = (newParams: Record<string, number>) => {
    const existingParams: Record<string, number> = {};
    const currentResult = resultRef.current;
    if (currentResult && currentResult.parameters) {
      const map: Record<string, string> = {
        "ph": "ph",
        "chlorine": "chlorine_residual_ppm",
        "turbidity": "turbidity_ntu",
        "nitrate": "nitrate_ppm",
        "nitrite": "nitrite_ppm",
        "hardness": "hardness_ppm",
        "iron": "iron_ppm"
      };
      currentResult.parameters.forEach(p => {
        const key = p.name.toLowerCase();
        if (map[key]) {
          existingParams[map[key]] = p.value;
        }
      });
    }
    
    // Normalize newParams keys just in case the LLM outputs "pH" instead of "ph", etc.
    const normalizedNewParams: Record<string, number> = {};
    Object.entries(newParams).forEach(([k, v]) => {
      const lowerK = k.toLowerCase();
      if (lowerK === 'ph') normalizedNewParams['ph'] = v;
      else if (lowerK.includes('chlorine')) normalizedNewParams['chlorine_residual_ppm'] = v;
      else if (lowerK.includes('turbidity')) normalizedNewParams['turbidity_ntu'] = v;
      else if (lowerK.includes('nitrate')) normalizedNewParams['nitrate_ppm'] = v;
      else if (lowerK.includes('nitrite')) normalizedNewParams['nitrite_ppm'] = v;
      else if (lowerK.includes('hardness')) normalizedNewParams['hardness_ppm'] = v;
      else if (lowerK.includes('iron')) normalizedNewParams['iron_ppm'] = v;
      else normalizedNewParams[k] = v;
    });

    const mergedParams = { ...existingParams, ...normalizedNewParams };
    handleManualSubmit(mergedParams);
  };

  return (
    <div className="relative z-10 min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-20 border-b border-line/70 bg-paper/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link
            href="/"
            className="group flex items-center gap-2 text-sm font-medium text-ink-soft transition-colors hover:text-ink"
          >
            <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
            Home
          </Link>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-water-400">
              <Droplets className="h-4 w-4 text-white" />
            </div>
            <span className="font-display text-base font-semibold text-ink">
              WaterForAll
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-6 px-6 py-8">
        {/* Title + location */}
        <div className="flex flex-col gap-4 rounded-3xl border border-line bg-paper p-6 shadow-sm lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="font-display text-3xl font-semibold tracking-tight text-ink">
              Water analysis
            </h1>
            <p className="mt-1 text-sm text-ink-soft">
              Screen a sample and get clear, source-backed guidance.
            </p>
          </div>
          <div className="lg:w-[420px]">
            <LocationSelector areaId={areaId} onChange={setAreaId} />
          </div>
        </div>

        {/* Input + orchestration */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <SampleInput
              activeScenario={activeScenario}
              running={running}
              onScenario={handleScenario}
              onUpload={handleUpload}
              onManualSubmit={handleManualSubmit}
            />
          </div>
          <AgentOrchestration activeIndex={activeIndex} running={running} />
        </div>

        {/* Diagnosis */}
        <DiagnosisPanel result={result} running={running} onReevaluate={handleManualSubmit} />

        {/* Community */}
        <CommunityRisk areaId={areaId} />
      </main>

      <ChatAssistant 
        activeScenario={activeScenario} 
        result={result} 
        onUpdateParams={handleChatUpdateParams} 
      />
    </div>
  );
}
