"use client";

import { motion } from "framer-motion";
import { AlertTriangle, BookOpen, FlaskConical } from "lucide-react";
import type { WaterTestResult } from "@/types";
import { riskThemes } from "@/lib/risk";
import { ConfidenceRing } from "./ConfidenceRing";

interface DiagnosisPanelProps {
  result: WaterTestResult | null;
  running: boolean;
}

export function DiagnosisPanel({ result, running }: DiagnosisPanelProps) {
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
          <p className="text-sm text-ink-soft">
            Water appears {result.waterAppearance}
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
