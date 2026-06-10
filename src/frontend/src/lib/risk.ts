import type { RiskLevel } from "@/types";

export interface RiskTheme {
  label: string;
  text: string;
  bg: string;
  border: string;
  dot: string;
  hex: string;
}

export const riskThemes: Record<RiskLevel, RiskTheme> = {
  safe: {
    label: "Safe",
    text: "text-safe",
    bg: "bg-safe/10",
    border: "border-safe/30",
    dot: "bg-safe",
    hex: "#3f8f5b",
  },
  caution: {
    label: "Caution",
    text: "text-caution",
    bg: "bg-caution/10",
    border: "border-caution/30",
    dot: "bg-caution",
    hex: "#c9892b",
  },
  unsafe: {
    label: "Unsafe",
    text: "text-unsafe",
    bg: "bg-unsafe/10",
    border: "border-unsafe/30",
    dot: "bg-unsafe",
    hex: "#c4452f",
  },
  unknown: {
    label: "Unknown",
    text: "text-ink-soft",
    bg: "bg-paper-soft",
    border: "border-line",
    dot: "bg-ink-soft",
    hex: "#5c6b64",
  },
};
