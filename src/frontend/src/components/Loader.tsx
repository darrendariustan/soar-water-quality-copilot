"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface LoaderProps {
  onComplete: () => void;
}

export function Loader({ onComplete }: LoaderProps) {
  const [progress, setProgress] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          clearInterval(interval);
          return 100;
        }
        const step = Math.max(1, Math.round((100 - p) / 14));
        return Math.min(100, p + step);
      });
    }, 55);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (progress >= 100) {
      const t = setTimeout(() => setDone(true), 450);
      return () => clearTimeout(t);
    }
  }, [progress]);

  return (
    <AnimatePresence onExitComplete={onComplete}>
      {!done && (
        <motion.div
          exit={{ opacity: 0 }}
          transition={{ duration: 0.7 }}
          className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-paper"
        >
          {/* Water-fill droplet */}
          <div className="relative h-32 w-32">
            <svg viewBox="0 0 100 100" className="absolute inset-0">
              <defs>
                <clipPath id="drop">
                  <path d="M50 6 C50 6 84 44 84 66 A34 34 0 0 1 16 66 C16 44 50 6 50 6 Z" />
                </clipPath>
              </defs>
              <path
                d="M50 6 C50 6 84 44 84 66 A34 34 0 0 1 16 66 C16 44 50 6 50 6 Z"
                fill="none"
                stroke="#ddd1bb"
                strokeWidth="2.5"
              />
              <g clipPath="url(#drop)">
                <motion.rect
                  x="0"
                  width="100"
                  height="100"
                  fill="#209dd7"
                  initial={{ y: 100 }}
                  animate={{ y: 100 - progress }}
                  transition={{ ease: "linear", duration: 0.1 }}
                />
                {/* subtle wave crest */}
                <motion.ellipse
                  cx="50"
                  rx="60"
                  ry="6"
                  fill="#54c3ed"
                  opacity="0.6"
                  initial={{ cy: 100 }}
                  animate={{ cy: 100 - progress }}
                  transition={{ ease: "linear", duration: 0.1 }}
                />
              </g>
            </svg>
          </div>

          <div className="mt-8 text-center">
            <p className="font-display text-5xl font-semibold tabular-nums text-ink">
              {progress}
              <span className="text-2xl text-ink-soft">%</span>
            </p>
            <p className="eyebrow mt-3 text-ink-soft">Preparing your check</p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
