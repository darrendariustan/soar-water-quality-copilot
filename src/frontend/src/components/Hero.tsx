"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Droplet } from "lucide-react";
import { Contour } from "./Contour";

const ease = [0.22, 1, 0.36, 1] as const;

export function Hero() {
  return (
    <section
      id="top"
      className="relative overflow-hidden px-6 pt-16 pb-24 sm:pt-24 sm:pb-32"
    >
      {/* Atmosphere */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute -top-32 -right-24 h-96 w-96 animate-float rounded-full bg-water-100/60 blur-3xl" />
        <div
          className="absolute bottom-0 -left-20 h-80 w-80 animate-float rounded-full bg-clay-soft/20 blur-3xl"
          style={{ animationDelay: "4s" }}
        />
        <Contour className="absolute -right-10 top-20 h-[440px] w-[440px] text-water-400/30" />
      </div>

      <div className="mx-auto grid max-w-6xl grid-cols-1 items-end gap-10 lg:grid-cols-12">
        {/* Headline column */}
        <div className="lg:col-span-8">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease }}
            className="flex items-center gap-3"
          >
            <span className="eyebrow text-clay">A first-level water check</span>
            <span className="h-px w-12 bg-line" />
          </motion.div>

          <h1 className="mt-6 font-display text-5xl font-semibold leading-[1.02] tracking-tight text-ink sm:text-7xl">
            {["Clean water", "shouldn't depend", "on where"].map((line, i) => (
              <motion.span
                key={line}
                initial={{ opacity: 0, y: 26 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.1 + i * 0.1, ease }}
                className="block"
              >
                {line}
              </motion.span>
            ))}
            <motion.span
              initial={{ opacity: 0, y: 26 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.4, ease }}
              className="block italic"
            >
              you <span className="shimmer-text">live.</span>
            </motion.span>
          </h1>
        </div>

        {/* Supporting column */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.5, ease }}
          className="lg:col-span-4"
        >
          <div className="flex items-start gap-3">
            <Droplet className="mt-1 h-5 w-5 flex-shrink-0 text-water-400" />
            <p className="text-base leading-relaxed text-ink-soft">
              Millions rely on water they cannot easily test. WaterForAll turns a
              phone photo and a low-cost test strip into a clear, honest read on
              whether your water is safe, and what to do next.
            </p>
          </div>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row lg:flex-col">
            <Link
              href="/app"
              className="group flex items-center justify-center gap-2 rounded-full bg-water-400 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-water-400/25 transition-colors hover:bg-water-500"
            >
              Try the demo
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
            <a
              href="#how"
              className="flex items-center justify-center rounded-full border border-line bg-paper px-6 py-3.5 text-sm font-semibold text-ink transition-colors hover:border-water-300"
            >
              See how it works
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
