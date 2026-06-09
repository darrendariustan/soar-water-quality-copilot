/**
 * Faint topographic contour motif. Evokes maps, terrain, and water depth.
 * Purely decorative atmosphere.
 */
export function Contour({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 400 400"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <g stroke="currentColor" strokeWidth="1" opacity="0.5">
        <path d="M30 200 Q120 120 200 200 T370 200" />
        <path d="M20 230 Q120 140 200 230 T380 230" />
        <path d="M10 260 Q120 160 200 260 T390 260" />
        <path d="M40 170 Q120 100 200 170 T360 170" />
        <path d="M55 140 Q125 85 200 140 T345 140" />
        <path d="M75 110 Q130 70 200 110 T325 110" />
      </g>
    </svg>
  );
}
