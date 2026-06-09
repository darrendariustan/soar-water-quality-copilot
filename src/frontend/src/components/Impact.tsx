"use client";

import { useEffect, useRef, useState } from "react";
import { useInView } from "framer-motion";
import { stats, type Stat } from "@/lib/content";
import { Reveal } from "./Reveal";

function Counter({ stat }: { stat: Stat }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (!inView) return;
    const duration = 1300;
    const start = performance.now();
    let frame: number;

    const tick = (now: number) => {
      const progress = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(eased * stat.value));
      if (progress < 1) frame = requestAnimationFrame(tick);
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [inView, stat.value]);

  return (
    <span ref={ref} className="tabular-nums">
      {value}
      {stat.suffix}
    </span>
  );
}

export function Impact() {
  return (
    <section id="impact" className="px-6 py-28">
      <div className="mx-auto max-w-6xl">
        <Reveal className="max-w-2xl">
          <div className="flex items-center gap-3">
            <span className="eyebrow text-clay">03 / Impact</span>
            <span className="h-px w-12 bg-line" />
          </div>
          <h2 className="mt-5 font-display text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
            Built for trust
          </h2>
          <p className="mt-4 max-w-md text-ink-soft">
            A first-level screening tool that is fast, transparent, and always
            points back to credible guidance.
          </p>
        </Reveal>

        <div className="mt-16 grid grid-cols-1 divide-y divide-line border-y border-line sm:grid-cols-2 sm:divide-y-0 lg:grid-cols-4">
          {stats.map((stat, i) => (
            <Reveal
              key={stat.label}
              delay={i * 0.1}
              className="border-line py-8 sm:px-8 sm:[&:not(:nth-child(2n))]:border-r lg:[&:not(:last-child)]:border-r"
            >
              <p className="font-display text-6xl font-semibold leading-none text-water-400">
                <Counter stat={stat} />
              </p>
              <p className="mt-4 text-sm leading-snug text-ink-soft">
                {stat.label}
              </p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
