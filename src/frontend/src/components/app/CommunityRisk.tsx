"use client";

import { useEffect, useState } from "react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { TrendingUp, TrendingDown, Minus, MapPin } from "lucide-react";
import type { CommunityRiskData } from "@/types";
import { getCommunityRisk } from "@/lib/api";
import { communityAreas } from "@/lib/mock-data";

interface CommunityRiskProps {
  areaId: string | null;
}

function TrendBadge({ trend }: { trend: CommunityRiskData["trend"] }) {
  if (trend === "improving")
    return (
      <span className="flex items-center gap-1 text-xs font-medium text-safe">
        <TrendingDown className="h-3.5 w-3.5" /> Improving
      </span>
    );
  if (trend === "worsening")
    return (
      <span className="flex items-center gap-1 text-xs font-medium text-unsafe">
        <TrendingUp className="h-3.5 w-3.5" /> Worsening
      </span>
    );
  return (
    <span className="flex items-center gap-1 text-xs font-medium text-ink-soft">
      <Minus className="h-3.5 w-3.5" /> Stable
    </span>
  );
}

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-line bg-paper px-3 py-2 text-xs shadow-md">
      {label && <p className="mb-1 text-ink-soft">{label}</p>}
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  );
}

export function CommunityRisk({ areaId }: CommunityRiskProps) {
  const [data, setData] = useState<CommunityRiskData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!areaId) {
      setData(null);
      return;
    }
    setLoading(true);
    getCommunityRisk(areaId).then((d) => {
      setData(d);
      setLoading(false);
    });
  }, [areaId]);

  const areaName = communityAreas.find((a) => a.id === areaId)?.name;

  return (
    <div className="rounded-3xl border border-line bg-paper p-6 shadow-sm">
      <div className="flex items-center gap-3">
        <span className="eyebrow text-clay">Community risk</span>
        <span className="h-px flex-1 bg-line" />
      </div>

      {!areaId ? (
        <div className="mt-6 flex items-center gap-3 rounded-2xl bg-paper-soft px-4 py-6 text-sm text-ink-soft">
          <MapPin className="h-5 w-5 text-water-400" />
          Select your area above to see local water safety trends and hotspots.
        </div>
      ) : loading || !data ? (
        <p className="mt-6 text-sm text-ink-soft">Loading community data...</p>
      ) : (
        <>
          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="font-display text-2xl font-semibold text-ink">
                {areaName}
              </h2>
              <p className="text-sm text-ink-soft">
                <span className="font-semibold text-unsafe">
                  {data.unsafeReadings}
                </span>{" "}
                of {data.totalReadings} recent readings unsafe
              </p>
            </div>
            <TrendBadge trend={data.trend} />
          </div>

          {/* Escalation note */}
          <div
            className={`mt-4 rounded-2xl border px-4 py-3 text-sm ${
              data.trend === "worsening"
                ? "border-unsafe/25 bg-unsafe/5 text-ink"
                : "border-line bg-paper-soft text-ink-soft"
            }`}
          >
            {data.escalation}
          </div>

          {/* Charts */}
          <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-line bg-paper-soft/40 p-4">
              <h3 className="mb-3 text-sm font-semibold text-ink">
                Safe vs unsafe over time
              </h3>
              <ResponsiveContainer width="100%" height={180}>
                <AreaChart data={data.history}>
                  <defs>
                    <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3f8f5b" stopOpacity={0.45} />
                      <stop offset="100%" stopColor="#3f8f5b" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="ug" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#c4452f" stopOpacity={0.45} />
                      <stop offset="100%" stopColor="#c4452f" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ddd1bb" />
                  <XAxis dataKey="month" stroke="#5c6b64" fontSize={11} />
                  <YAxis stroke="#5c6b64" fontSize={11} />
                  <Tooltip content={<ChartTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="safe"
                    name="Safe"
                    stroke="#3f8f5b"
                    fill="url(#sg)"
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey="unsafe"
                    name="Unsafe"
                    stroke="#c4452f"
                    fill="url(#ug)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="rounded-2xl border border-line bg-paper-soft/40 p-4">
              <h3 className="mb-3 text-sm font-semibold text-ink">
                Common parameter failures
              </h3>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={data.parameterFailures} layout="vertical">
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#ddd1bb"
                    horizontal={false}
                  />
                  <XAxis type="number" stroke="#5c6b64" fontSize={11} />
                  <YAxis
                    type="category"
                    dataKey="parameter"
                    stroke="#5c6b64"
                    fontSize={11}
                    width={70}
                  />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: "#ece4d480" }} />
                  <Bar
                    dataKey="failures"
                    name="Failures"
                    fill="#209dd7"
                    radius={[0, 4, 4, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
