"use client";

import { useState } from "react";
import { MapPin, LocateFixed, Loader2 } from "lucide-react";
import { communityAreas } from "@/lib/mock-data";

interface LocationSelectorProps {
  areaId: string | null;
  onChange: (areaId: string | null) => void;
}

export function LocationSelector({ areaId, onChange }: LocationSelectorProps) {
  const [detecting, setDetecting] = useState(false);

  const handleDetect = () => {
    if (!navigator.geolocation) return;
    setDetecting(true);
    navigator.geolocation.getCurrentPosition(
      () => {
        // In production this would reverse-geocode to a coarse area.
        // For the demo we map any detected location to the nearest sample area.
        onChange(communityAreas[0].id);
        setDetecting(false);
      },
      () => setDetecting(false),
      { timeout: 8000 }
    );
  };

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div className="flex items-center gap-2 text-ink-soft">
        <MapPin className="h-4 w-4 text-water-400" />
        <span className="text-sm font-medium text-ink">Your area</span>
        <span className="rounded-full bg-paper-soft px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-ink-soft">
          Optional
        </span>
      </div>

      <div className="flex flex-1 items-center gap-2">
        <select
          value={areaId ?? ""}
          onChange={(e) => onChange(e.target.value || null)}
          className="flex-1 rounded-xl border border-line bg-paper px-3 py-2 text-sm text-ink focus:border-water-400 focus:outline-none"
        >
          <option value="">Not specified</option>
          {communityAreas.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name} — {a.region}
            </option>
          ))}
        </select>

        <button
          onClick={handleDetect}
          disabled={detecting}
          className="flex items-center gap-1.5 rounded-xl border border-line bg-paper px-3 py-2 text-sm text-ink-soft transition-colors hover:border-water-300 hover:text-water-500 disabled:opacity-50"
        >
          {detecting ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <LocateFixed className="h-4 w-4" />
          )}
          <span className="hidden sm:inline">Detect</span>
        </button>
      </div>
    </div>
  );
}
