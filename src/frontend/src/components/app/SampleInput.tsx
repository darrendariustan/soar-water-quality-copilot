"use client";

import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Droplets,
  Bug,
  FlaskConical,
  ImageIcon,
  Loader2,
  X,
} from "lucide-react";
import type { ScenarioId } from "@/types";

interface SampleInputProps {
  activeScenario: ScenarioId | null;
  running: boolean;
  onScenario: (s: ScenarioId) => void;
  onUpload: (waterImage: File, testStripImage?: File) => void;
  onManualSubmit?: (params: Record<string, number>) => void;
}

const scenarios: {
  id: ScenarioId;
  label: string;
  desc: string;
  icon: typeof Droplets;
  tone: string;
}[] = [
  {
    id: "safe",
    label: "Safe Water",
    desc: "Clear sample, all in range",
    icon: Droplets,
    tone: "text-safe",
  },
  {
    id: "microbial",
    label: "Microbial Outbreak",
    desc: "Cloudy, high turbidity",
    icon: Bug,
    tone: "text-caution",
  },
  {
    id: "chemical",
    label: "Chemical Spill",
    desc: "Colored, low pH, high nitrate",
    icon: FlaskConical,
    tone: "text-unsafe",
  },
];

function DropZone({
  label,
  preview,
  onFile,
  onClear,
}: {
  label: string;
  preview: string | null;
  onFile: (f: File) => void;
  onClear: () => void;
}) {
  const [dragging, setDragging] = useState(false);
  return (
    <div>
      <label className="mb-2 block text-xs font-medium text-ink-soft">
        {label}
      </label>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const f = e.dataTransfer.files[0];
          if (f) onFile(f);
        }}
        className={`relative flex min-h-[130px] items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed transition-colors ${
          dragging
            ? "border-water-400 bg-water-50"
            : "border-line hover:border-water-300"
        }`}
      >
        {preview ? (
          <>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={preview}
              alt={`${label} preview`}
              className="max-h-32 w-full object-contain"
            />
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onClear();
              }}
              className="absolute right-2 top-2 z-10 rounded-full bg-paper/90 p-1 text-ink-soft hover:text-ink"
              aria-label="Remove image"
            >
              <X className="h-4 w-4" />
            </button>
          </>
        ) : (
          <div className="pointer-events-none px-4 py-6 text-center">
            <ImageIcon className="mx-auto mb-2 h-7 w-7 text-line" />
            <p className="text-sm text-ink-soft">Drop or click</p>
          </div>
        )}
        <input
          type="file"
          accept="image/*"
          className={`absolute inset-0 cursor-pointer opacity-0 ${preview ? 'hidden' : ''}`}
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) onFile(f);
          }}
        />
      </div>
    </div>
  );
}

export function SampleInput({
  activeScenario,
  running,
  onScenario,
  onUpload,
  onManualSubmit,
}: SampleInputProps) {
  const [waterImage, setWaterImage] = useState<File | null>(null);
  const [stripImage, setStripImage] = useState<File | null>(null);
  const [waterPreview, setWaterPreview] = useState<string | null>(null);
  const [stripPreview, setStripPreview] = useState<string | null>(null);

  const [isManualMode, setIsManualMode] = useState(false);
  const [manualParams, setManualParams] = useState({
    turbidity_ntu: 0,
    chlorine_residual_ppm: 0,
    ph: 7.0,
    nitrate_ppm: 0,
  });

  const read = useCallback(
    (file: File, setter: (p: string | null) => void) => {
      const reader = new FileReader();
      reader.onload = (e) => setter(e.target?.result as string);
      reader.readAsDataURL(file);
    },
    []
  );

  return (
    <div className="rounded-3xl border border-line bg-paper p-6 shadow-sm">
      <div className="flex items-center gap-3">
        <span className="eyebrow text-clay">Live demo</span>
        <span className="h-px flex-1 bg-line" />
      </div>
      <h2 className="mt-3 font-display text-2xl font-semibold text-ink">
        Test a water sample
      </h2>
      <p className="mt-1 text-sm text-ink-soft">
        Trigger a preset scenario, or upload your own photos.
      </p>

      {/* Scenario presets */}
      <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-3">
        {scenarios.map((s, i) => {
          const Icon = s.icon;
          const isActive = activeScenario === s.id;
          return (
            <motion.button
              key={s.id}
              whileHover={{ scale: running ? 1 : 1.02 }}
              whileTap={{ scale: running ? 1 : 0.98 }}
              onClick={() => !running && onScenario(s.id)}
              disabled={running}
              transition={{ delay: i * 0.05 }}
              className={`rounded-2xl border bg-paper p-4 text-left transition-colors disabled:cursor-not-allowed ${
                isActive
                  ? "border-water-400 ring-1 ring-water-400/30"
                  : "border-line hover:border-water-300"
              }`}
            >
              <Icon className={`mb-2 h-5 w-5 ${s.tone}`} />
              <p className="text-sm font-semibold text-ink">{s.label}</p>
              <p className="mt-0.5 text-xs leading-snug text-ink-soft">
                {s.desc}
              </p>
            </motion.button>
          );
        })}
      </div>

      {/* Divider */}
      <div className="my-6 flex items-center gap-3">
        <span className="h-px flex-1 bg-line" />
        <span className="text-xs uppercase tracking-wider text-ink-soft">
          or upload
        </span>
        <button
          onClick={() => setIsManualMode(!isManualMode)}
          className="rounded-full bg-paper-soft px-3 py-1 text-xs font-medium text-ink transition-colors hover:bg-line/50"
        >
          {isManualMode ? "Switch to Photos" : "Manual Entry"}
        </button>
        <span className="h-px flex-1 bg-line" />
      </div>

      {/* Upload zones or Manual Entry */}
      {isManualMode ? (
        <div className="space-y-5 rounded-2xl border border-line p-5">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium text-ink">Turbidity (NTU)</span>
              <span className="font-mono text-ink-soft">{manualParams.turbidity_ntu.toFixed(1)}</span>
            </div>
            <input type="range" min="0" max="20" step="0.5" value={manualParams.turbidity_ntu} onChange={(e) => setManualParams({...manualParams, turbidity_ntu: parseFloat(e.target.value)})} className="w-full accent-water-400" />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium text-ink">Chlorine (ppm)</span>
              <span className="font-mono text-ink-soft">{manualParams.chlorine_residual_ppm.toFixed(1)}</span>
            </div>
            <input type="range" min="0" max="5" step="0.1" value={manualParams.chlorine_residual_ppm} onChange={(e) => setManualParams({...manualParams, chlorine_residual_ppm: parseFloat(e.target.value)})} className="w-full accent-water-400" />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium text-ink">pH</span>
              <span className="font-mono text-ink-soft">{manualParams.ph.toFixed(1)}</span>
            </div>
            <input type="range" min="0" max="14" step="0.1" value={manualParams.ph} onChange={(e) => setManualParams({...manualParams, ph: parseFloat(e.target.value)})} className="w-full accent-water-400" />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium text-ink">Nitrate (ppm)</span>
              <span className="font-mono text-ink-soft">{manualParams.nitrate_ppm.toFixed(0)}</span>
            </div>
            <input type="range" min="0" max="50" step="1" value={manualParams.nitrate_ppm} onChange={(e) => setManualParams({...manualParams, nitrate_ppm: parseFloat(e.target.value)})} className="w-full accent-water-400" />
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <DropZone
            label="Water photo"
            preview={waterPreview}
            onFile={(f) => {
              setWaterImage(f);
              read(f, setWaterPreview);
            }}
            onClear={() => {
              setWaterImage(null);
              setWaterPreview(null);
            }}
          />
          <DropZone
            label="Test strip photo (optional)"
            preview={stripPreview}
            onFile={(f) => {
              setStripImage(f);
              read(f, setStripPreview);
            }}
            onClear={() => {
              setStripImage(null);
              setStripPreview(null);
            }}
          />
        </div>
      )}

      <motion.button
        whileHover={{ scale: (isManualMode || waterImage) && !running ? 1.01 : 1 }}
        whileTap={{ scale: (isManualMode || waterImage) && !running ? 0.99 : 1 }}
        onClick={() => {
          if (isManualMode && onManualSubmit) {
            onManualSubmit(manualParams);
          } else if (waterImage) {
            onUpload(waterImage, stripImage || undefined);
          }
        }}
        disabled={(!isManualMode && !waterImage) || running}
        className="mt-5 w-full rounded-full bg-water-400 px-4 py-3 text-sm font-semibold text-white shadow-md shadow-water-400/20 transition-colors hover:bg-water-500 disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
      >
        {running ? (
          <span className="flex items-center justify-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            Analyzing...
          </span>
        ) : (
          "Analyze sample"
        )}
      </motion.button>
    </div>
  );
}
