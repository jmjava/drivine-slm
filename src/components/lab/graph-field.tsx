export function GraphField() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="graph-wash absolute inset-0" />
      <svg className="absolute inset-0 h-full w-full opacity-[0.35]" viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid slice">
        <defs>
          <radialGradient id="nodeGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="var(--signal)" stopOpacity="0.55" />
            <stop offset="100%" stopColor="var(--signal)" stopOpacity="0" />
          </radialGradient>
        </defs>
        <g stroke="var(--edge)" strokeWidth="1" fill="none">
          <path className="edge-draw" d="M120 160 C280 120, 340 260, 520 220" />
          <path className="edge-draw edge-delay-1" d="M520 220 C700 170, 760 320, 980 280" />
          <path className="edge-draw edge-delay-2" d="M520 220 C480 360, 620 480, 780 520" />
          <path className="edge-draw edge-delay-3" d="M220 480 C360 420, 420 560, 620 540" />
          <path className="edge-draw" d="M780 520 C900 560, 980 420, 1080 460" />
        </g>
        <g fill="var(--ink)">
          <circle className="node-pulse" cx="120" cy="160" r="7" />
          <circle className="node-pulse node-delay-1" cx="520" cy="220" r="10" />
          <circle className="node-pulse node-delay-2" cx="980" cy="280" r="7" />
          <circle className="node-pulse node-delay-3" cx="780" cy="520" r="9" />
          <circle className="node-pulse" cx="220" cy="480" r="6" />
          <circle className="node-pulse node-delay-2" cx="1080" cy="460" r="6" />
        </g>
        <circle cx="520" cy="220" r="28" fill="url(#nodeGlow)" />
        <circle cx="780" cy="520" r="24" fill="url(#nodeGlow)" />
      </svg>
    </div>
  );
}
