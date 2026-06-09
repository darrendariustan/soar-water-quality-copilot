"use client";

import { steps } from "@/lib/content";
import { Reveal } from "./Reveal";

export function HowItWorks() {
  return (
    <section id="how" className="relative px-6 py-28">
      <div className="mx-auto max-w-6xl">
        <Reveal className="max-w-2xl">
          <div className="flex items-center gap-3">
            <span className="eyebrow text-clay">01 / How it works</span>
            <span className="h-px w-12 bg-line" />
          </div>
          <h2 className="mt-5 font-display text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
            Three simple steps
          </h2>
          <p className="mt-4 max-w-md text-ink-soft">
            No lab, no sensors, no training required. Just a phone and a test
            strip.
          </p>
        </Reveal>

        <div className="mt-16 grid grid-cols-1 gap-x-8 gap-y-12 md:grid-cols-3">
          {steps.map((step, i) => {
            const Icon = step.icon;
            return (
              <Reveal
                key={step.title}
                delay={i * 0.12}
                className={i % 2 === 1 ? "md:mt-12" : ""}
              >
                <div className="group relative">
                  {/* Oversized step number */}
                  <span className="font-display text-7xl font-semibold leading-none text-paper-deep transition-colors group-hover:text-water-100">
                    0{i + 1}
                  </span>

                  <div className="mt-4 flex h-12 w-12 items-center justify-center rounded-2xl border border-line bg-paper text-water-400 shadow-sm">
                    <Icon className="h-6 w-6" />
                  </div>

                  <h3 className="mt-5 font-display text-2xl font-semibold text-ink">
                    {step.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-ink-soft">
                    {step.description}
                  </p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
