"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus } from "lucide-react";
import { agents } from "@/lib/content";
import { Reveal } from "./Reveal";
import { Contour } from "./Contour";

export function Agents() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section
      id="agents"
      className="relative overflow-hidden bg-paper-soft px-6 py-28"
    >
      <Contour className="pointer-events-none absolute -left-16 bottom-0 h-[420px] w-[420px] text-clay/20" />

      <div className="mx-auto max-w-6xl">
        <Reveal className="max-w-2xl">
          <div className="flex items-center gap-3">
            <span className="eyebrow text-clay">02 / The agents</span>
            <span className="h-px w-12 bg-line" />
          </div>
          <h2 className="mt-5 font-display text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
            A team that works together
          </h2>
          <p className="mt-4 max-w-lg text-ink-soft">
            Nine specialized agents work under a master coordinator, each
            handling one part of the job so every recommendation stays grounded
            and safe. Here are the six doing the heaviest lifting. Tap a card to
            learn more.
          </p>
        </Reveal>

        <div className="mt-14 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent, i) => {
            const Icon = agent.icon;
            const isOpen = open === i;
            return (
              <Reveal key={agent.name} delay={(i % 3) * 0.08}>
                <button
                  onClick={() => setOpen(isOpen ? null : i)}
                  className={`flex h-full w-full flex-col rounded-3xl border bg-paper p-6 text-left transition-all ${
                    isOpen
                      ? "border-water-300 shadow-lg shadow-water-400/10"
                      : "border-line hover:-translate-y-0.5 hover:border-water-200 hover:shadow-md"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-water-50 text-water-400">
                      <Icon className="h-5 w-5" />
                    </div>
                    <motion.span
                      animate={{ rotate: isOpen ? 135 : 0 }}
                      transition={{ duration: 0.3 }}
                      className="text-ink-soft"
                    >
                      <Plus className="h-5 w-5" />
                    </motion.span>
                  </div>

                  <h3 className="mt-5 font-display text-xl font-semibold text-ink">
                    {agent.name}
                  </h3>
                  <p className="mt-1 text-sm font-medium text-water-500">
                    {agent.role}
                  </p>

                  <AnimatePresence initial={false}>
                    {isOpen && (
                      <motion.p
                        initial={{ height: 0, opacity: 0, marginTop: 0 }}
                        animate={{ height: "auto", opacity: 1, marginTop: 14 }}
                        exit={{ height: 0, opacity: 0, marginTop: 0 }}
                        transition={{ duration: 0.3 }}
                        className="overflow-hidden text-sm leading-relaxed text-ink-soft"
                      >
                        {agent.detail}
                      </motion.p>
                    )}
                  </AnimatePresence>
                </button>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
