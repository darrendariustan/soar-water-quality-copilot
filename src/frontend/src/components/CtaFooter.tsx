"use client";

import Link from "next/link";
import { ArrowRight, Droplets } from "lucide-react";
import { Reveal } from "./Reveal";
import { Contour } from "./Contour";

export function CtaFooter() {
  return (
    <footer className="relative overflow-hidden bg-ink px-6 pt-28 pb-10 text-paper">
      <Contour className="pointer-events-none absolute -right-20 -top-10 h-[500px] w-[500px] text-water-300/15" />

      <div className="mx-auto max-w-6xl">
        {/* CTA */}
        <Reveal className="max-w-3xl">
          <h2 className="font-display text-4xl font-semibold leading-tight tracking-tight sm:text-6xl">
            See your water&apos;s story in{" "}
            <span className="italic text-water-300">seconds.</span>
          </h2>
          <p className="mt-5 max-w-lg text-paper/70">
            Walk through the full experience, from photo to plain-language
            guidance, in the live demo.
          </p>
          <Link
            href="/app"
            className="group mt-8 inline-flex items-center gap-2 rounded-full bg-water-400 px-7 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-water-300"
          >
            Try the demo
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </Reveal>

        {/* Footer bar */}
        <div className="mt-24 flex flex-col items-start justify-between gap-6 border-t border-paper/15 pt-8 sm:flex-row sm:items-center">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-water-400">
              <Droplets className="h-4 w-4 text-white" />
            </div>
            <span className="font-display text-lg font-semibold">
              WaterForAll
            </span>
          </div>
          <p className="text-xs text-paper/50">
            A first-level water safety screening tool. Not a replacement for
            laboratory testing.
          </p>
        </div>
      </div>
    </footer>
  );
}
