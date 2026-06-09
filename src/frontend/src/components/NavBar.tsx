"use client";

import Link from "next/link";

const links = [
  { label: "01 / How", href: "#how" },
  { label: "02 / Agents", href: "#agents" },
  { label: "03 / Impact", href: "#impact" },
];

export function NavBar() {
  return (
    <header className="sticky top-0 z-40 border-b border-line/70 bg-paper/85 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="#top" className="flex items-baseline gap-2">
          <span className="font-display text-xl font-semibold tracking-tight text-ink">
            WaterForAll
          </span>
          <span className="h-2 w-2 rounded-full bg-water-400" />
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-xs font-semibold uppercase tracking-[0.18em] text-ink-soft transition-colors hover:text-water-400"
            >
              {l.label}
            </a>
          ))}
        </div>

        <Link
          href="/app"
          className="group relative overflow-hidden rounded-full border border-ink px-5 py-2 text-sm font-medium text-ink transition-colors hover:text-paper"
        >
          <span className="relative z-10">Try the demo</span>
          <span className="absolute inset-0 -z-0 origin-left scale-x-0 bg-ink transition-transform duration-300 group-hover:scale-x-100" />
        </Link>
      </nav>
    </header>
  );
}
