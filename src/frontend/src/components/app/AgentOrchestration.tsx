"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { agentPipeline } from "@/lib/mock-data";

interface AgentOrchestrationProps {
  activeIndex: number;
  running: boolean;
}

export function AgentOrchestration({
  activeIndex,
  running,
}: AgentOrchestrationProps) {
  const statusLabel = running
    ? "Processing"
    : activeIndex >= agentPipeline.length
      ? "Complete"
      : "Idle";

  return (
    <div className="rounded-3xl border border-line bg-paper p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-lg font-semibold text-ink">
          Agent orchestration
        </h2>
        <span className="rounded-full bg-paper-soft px-2.5 py-1 text-[10px] font-medium uppercase tracking-wide text-ink-soft">
          {statusLabel}
        </span>
      </div>

      <div className="mt-5 space-y-1">
        {agentPipeline.map((agent, i) => {
          const status =
            i < activeIndex
              ? "done"
              : i === activeIndex && running
                ? "active"
                : "idle";

          return (
            <div key={agent.id} className="flex items-start gap-3">
              <div className="relative flex-shrink-0">
                <motion.div
                  animate={{ scale: status === "active" ? [1, 1.12, 1] : 1 }}
                  transition={{
                    repeat: status === "active" ? Infinity : 0,
                    duration: 1.2,
                  }}
                  className={`flex h-7 w-7 items-center justify-center rounded-full border ${
                    status === "done"
                      ? "border-safe bg-safe/10 text-safe"
                      : status === "active"
                        ? "border-water-400 bg-water-50 text-water-500"
                        : "border-line bg-paper text-ink-soft"
                  }`}
                >
                  <AnimatePresence mode="wait">
                    {status === "done" ? (
                      <motion.span key="d" initial={{ scale: 0 }} animate={{ scale: 1 }}>
                        <Check className="h-3.5 w-3.5" />
                      </motion.span>
                    ) : status === "active" ? (
                      <motion.span key="a">
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      </motion.span>
                    ) : (
                      <motion.span key="i" className="text-[10px] font-semibold">
                        {i + 1}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </motion.div>
                {i < agentPipeline.length - 1 && (
                  <div
                    className={`absolute left-1/2 top-7 h-[18px] w-px -translate-x-1/2 ${
                      i < activeIndex ? "bg-safe/40" : "bg-line"
                    }`}
                  />
                )}
              </div>

              <div
                className={`flex-1 rounded-lg px-2 py-1 transition-colors ${
                  status === "active" ? "bg-water-50" : ""
                }`}
              >
                <p
                  className={`text-sm font-medium ${
                    status === "idle" ? "text-ink-soft" : "text-ink"
                  }`}
                >
                  {agent.name}
                </p>
                <p className="text-xs leading-tight text-ink-soft/70">
                  {agent.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
