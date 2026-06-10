import {
  Camera,
  ScanLine,
  Database,
  Globe,
  Sprout,
  ShieldCheck,
  type LucideIcon,
} from "lucide-react";

export interface Step {
  title: string;
  description: string;
  icon: LucideIcon;
}

export const steps: Step[] = [
  {
    title: "Take a photo",
    description:
      "Dip a low-cost test strip, then photograph your water and the strip with any phone.",
    icon: Camera,
  },
  {
    title: "We analyze it",
    description:
      "Computer vision reads the strip colors and water clarity, then specialized agents check the results against trusted guidance.",
    icon: ScanLine,
  },
  {
    title: "Get clear guidance",
    description:
      "You receive simple, honest next steps: settle, filter, boil, store safely, or seek another source.",
    icon: Sprout,
  },
];

export interface Agent {
  name: string;
  role: string;
  detail: string;
  icon: LucideIcon;
}

export const agents: Agent[] = [
  {
    name: "Computer Vision",
    role: "Reads the test strip and water",
    detail:
      "Interprets strip color changes against a reference chart and judges whether the water looks clear, cloudy, or colored, with a confidence score.",
    icon: ScanLine,
  },
  {
    name: "Water Quality",
    role: "Interprets the readings",
    detail:
      "Maps parameters like pH, turbidity, nitrate, and chlorine into plain categories: safe, caution, unsafe, or needs lab testing.",
    icon: Database,
  },
  {
    name: "Knowledge Retrieval",
    role: "Searches the safe-water database",
    detail:
      "Looks up curated, source-backed guidance stored in the AWS knowledge base so advice is grounded in real public-health references.",
    icon: Database,
  },
  {
    name: "Exa Web Crawl",
    role: "Pulls trusted public guidance",
    detail:
      "When the database is missing context for a region or contaminant, it crawls authoritative sources like WHO, CDC, and UNICEF.",
    icon: Globe,
  },
  {
    name: "Treatment Guidance",
    role: "Tells you what to do",
    detail:
      "Turns the diagnosis into practical household steps: settling, filtering, boiling, safe storage, or avoiding the water entirely.",
    icon: Sprout,
  },
  {
    name: "Safety & Compliance",
    role: "Keeps the advice safe",
    detail:
      "A hard gate that prevents unsafe recommendations, such as suggesting boiling for chemically contaminated water.",
    icon: ShieldCheck,
  },
];

export interface Stat {
  value: number;
  suffix: string;
  label: string;
}

export const stats: Stat[] = [
  { value: 8, suffix: "", label: "Water quality parameters screened" },
  { value: 9, suffix: "", label: "Specialized agents working together" },
  { value: 10, suffix: "s", label: "Typical time to a first-level result" },
  { value: 100, suffix: "%", label: "Recommendations traced to trusted sources" },
];