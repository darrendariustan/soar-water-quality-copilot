"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, BookOpen, FlaskConical, CheckCircle, XCircle, SlidersHorizontal, ShieldAlert } from "lucide-react";
import type { WaterTestResult } from "@/types";
import { riskThemes } from "@/lib/risk";
import { ConfidenceRing } from "./ConfidenceRing";

interface DiagnosisPanelProps {
  result: WaterTestResult | null;
  running: boolean;
  onReevaluate?: (params: Record<string, number>) => void;
}

export function DiagnosisPanel({ result, running, onReevaluate }: DiagnosisPanelProps) {
  const [reviewStatus, setReviewStatus] = useState<"pending" | "approved" | "vetoed">("pending");
  const [showAdjustParams, setShowAdjustParams] = useState(false);
  const [overrides, setOverrides] = useState<Record<string, number>>({});

  const getParamKey = (name: string) => {
    const key = name.toLowerCase();
    if (key.includes('ph')) return 'ph';
    if (key.includes('chlorine')) return 'chlorine_residual_ppm';
    if (key.includes('turbidity')) return 'turbidity_ntu';
    if (key.includes('nitrate')) return 'nitrate_ppm';
    if (key.includes('nitrite')) return 'nitrite_ppm';
    if (key.includes('hardness')) return 'hardness_ppm';
    if (key.includes('iron')) return 'iron_ppm';
    return key.replace(/\s+/g, '_');
  };

  const handleSaveReevaluate = () => {
    setShowAdjustParams(false);
    setReviewStatus("pending");
    if (onReevaluate && result) {
      const finalParams: Record<string, number> = {};
      result.parameters.forEach(p => {
        const key = getParamKey(p.name);
        finalParams[key] = overrides[key] !== undefined ? overrides[key] : p.value;
      });
      onReevaluate(finalParams);
    }
  };
  if (!result) {
    return (
      <div className="flex min-h-[340px] flex-col items-center justify-center rounded-3xl border border-line bg-paper p-8 text-center shadow-sm">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-paper-soft text-ink-soft">
          <FlaskConical className="h-7 w-7" />
        </div>
        <h2 className="mt-4 font-display text-xl font-semibold text-ink">
          {running ? "Reading your sample..." : "Awaiting a sample"}
        </h2>
        <p className="mt-2 max-w-xs text-sm text-ink-soft">
          {running
            ? "The agents are analyzing the water. Your diagnosis will appear here."
            : "Run a demo scenario or upload a sample to see the safety diagnosis."}
        </p>
      </div>
    );
  }

  const theme = riskThemes[result.overallRisk];

  return (
    <motion.div
      key={result.id}
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6 rounded-3xl border border-line bg-paper p-6 shadow-sm"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <span className="eyebrow text-clay">Diagnosis</span>
          <h2 className="mt-2 font-display text-2xl font-semibold text-ink">
            {result.scenarioLabel}
          </h2>
          <p className="mt-1 text-base text-ink-soft">
            Water appears{" "}
            <span
              className={`font-semibold ${
                result.waterAppearance === "clear" ? "text-ink" : "text-caution"
              }`}
            >
              {result.waterAppearance}
            </span>
          </p>
        </div>
        <ConfidenceRing value={result.confidence} color={theme.hex} />
      </div>

      {/* Risk banner */}
      <div className={`rounded-2xl border px-4 py-3 ${theme.bg} ${theme.border}`}>
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${theme.dot}`} />
          <span className={`text-sm font-semibold uppercase tracking-wide ${theme.text}`}>
            {theme.label}
          </span>
        </div>
        <p className="mt-1.5 text-sm leading-snug text-ink">{result.summary}</p>
      </div>

      {/* Parameters */}
      <div>
        <h3 className="mb-3 text-sm font-semibold text-ink">Parameter readings</h3>
        <div className="space-y-2.5">
          {result.parameters.map((p, i) => {
            const pt = riskThemes[p.riskLevel];
            return (
              <div key={p.name} className="flex items-center gap-3">
                <span className="w-20 shrink-0 text-xs text-ink-soft">{p.name}</span>
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-paper-soft">
                  <motion.div
                    className="h-full rounded-full"
                    style={{ backgroundColor: pt.hex }}
                    initial={{ width: 0 }}
                    animate={{ width: `${p.scale * 100}%` }}
                    transition={{ duration: 0.7, delay: i * 0.06 }}
                  />
                </div>
                <span className={`w-20 shrink-0 text-right text-xs font-medium ${pt.text}`}>
                  {p.value}
                  {p.unit && <span className="text-ink-soft"> {p.unit}</span>}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recommendations */}
      <div>
        <h3 className="mb-2 text-sm font-semibold text-ink">Recommended steps</h3>
        <ol className="space-y-1.5">
          {result.recommendations.map((rec, i) => (
            <motion.li
              key={i}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + i * 0.08 }}
              className="flex gap-2 text-sm text-ink"
            >
              <span className="shrink-0 font-semibold text-water-500">{i + 1}.</span>
              {rec}
            </motion.li>
          ))}
        </ol>
      </div>

      {/* Warnings */}
      {result.warnings.length > 0 && (
        <div className="rounded-2xl border border-unsafe/25 bg-unsafe/5 p-4">
          <div className="mb-1 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-unsafe" />
            <h3 className="text-sm font-semibold text-unsafe">Warning</h3>
          </div>
          {result.warnings.map((w, i) => (
            <p key={i} className="text-sm leading-snug text-ink">
              {w}
            </p>
          ))}
        </div>
      )}

      {/* Live Web Context (Exa) */}
      {result.exaContexts && result.exaContexts.length > 0 && (
        <div className="space-y-3 rounded-2xl border border-line bg-paper-soft p-4">
          <div className="flex items-center gap-2 border-b border-line pb-2">
            <BookOpen className="h-4 w-4 text-water-600" />
            <h3 className="text-sm font-semibold text-ink">Live Web Context</h3>
          </div>
          {result.exaContexts.map((ctx, i) => (
            <div key={i} className="space-y-1">
              <a
                href={ctx.url}
                target="_blank"
                rel="noreferrer"
                className="text-sm font-medium text-water-600 hover:underline"
              >
                {ctx.title}
              </a>
              {ctx.summary && (
                <p className="text-xs leading-relaxed text-ink-soft">
                  {ctx.summary}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Operator Review Controls */}
      <div className="mt-8 border-t border-line pt-6">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-water-600" />
            <h3 className="font-semibold text-ink">Operator Review</h3>
          </div>
          <span className={`text-xs font-medium uppercase tracking-wider ${
            reviewStatus === "approved" ? "text-safe" : reviewStatus === "vetoed" ? "text-unsafe" : "text-ink-soft"
          }`}>
            {reviewStatus}
          </span>
        </div>
        
        <p className="mb-4 text-sm text-ink-soft">
          Review the automated diagnosis. You can adjust parameters manually if the CV detection was inaccurate, or approve/veto this hazard alert before it is logged to the community database.
        </p>
        
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => setShowAdjustParams(!showAdjustParams)}
            className="flex items-center gap-2 rounded-xl border border-line bg-paper px-4 py-2 text-sm font-medium text-ink transition-colors hover:bg-paper-soft"
          >
            <SlidersHorizontal className="h-4 w-4" />
            Adjust Parameters
          </button>
          <button
            onClick={() => setReviewStatus("approved")}
            className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-colors ${
              reviewStatus === "approved"
                ? "bg-safe text-white"
                : "border border-safe/30 bg-safe/5 text-safe hover:bg-safe/10"
            }`}
          >
            <CheckCircle className="h-4 w-4" />
            Approve Alert
          </button>
          <button
            onClick={() => setReviewStatus("vetoed")}
            className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-colors ${
              reviewStatus === "vetoed"
                ? "bg-unsafe text-white"
                : "border border-unsafe/30 bg-unsafe/5 text-unsafe hover:bg-unsafe/10"
            }`}
          >
            <XCircle className="h-4 w-4" />
            Veto Alert
          </button>
        </div>

        {showAdjustParams && (
          <div className="mt-4 rounded-xl border border-line bg-paper-soft p-4">
            <p className="mb-3 text-sm font-medium text-ink">Manual Parameter Adjustment</p>
            <div className="space-y-3">
              {result.parameters.map(p => (
                <div key={p.name} className="flex items-center justify-between text-sm">
                  <span className="text-ink-soft">{p.name}</span>
                  <div className="flex items-center gap-2">
                    <input 
                      type="number" 
                      defaultValue={p.value}
                      onChange={(e) => setOverrides({...overrides, [getParamKey(p.name)]: parseFloat(e.target.value)})}
                      className="w-20 rounded border border-line bg-paper px-2 py-1 text-right text-ink focus:border-water-400 focus:outline-none"
                    />
                    <span className="w-8 text-xs text-ink-soft">{p.unit}</span>
                  </div>
                </div>
              ))}
              <button 
                onClick={handleSaveReevaluate}
                className="mt-2 w-full rounded-lg bg-water-500 py-2 text-sm font-medium text-white hover:bg-water-600"
              >
                Save & Re-evaluate
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Sources */}
      {result.sources.length > 0 && (
        <div className="flex items-start gap-2 border-t border-line pt-4 text-xs text-ink-soft">
          <BookOpen className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span>{result.sources.join(" · ")}</span>
        </div>
      )}
    </motion.div>
  );
}
