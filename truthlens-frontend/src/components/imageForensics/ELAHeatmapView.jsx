import SignalBadge from "../report/SignalBadge"

export default function ELAHeatmapView({ ela }) {
  return (
    <div className="bg-surface border border-border p-5 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs text-muted mb-1">SIGNAL 01 — ERROR LEVEL ANALYSIS</p>
          <p className="font-medium text-primary text-sm">{ela.verdict}</p>
        </div>
        <SignalBadge score={ela.suspicion_score} />
      </div>

      <div className="scanline specimen-frame bg-black">
        <img
          src={`data:image/png;base64,${ela.heatmap_base64}`}
          alt="ELA heatmap"
          className="w-full object-contain max-h-64"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Stat label="Mean Error" value={ela.mean_error} />
        <Stat label="Std Deviation" value={ela.std_error} />
      </div>

      <p className="text-xs text-secondary leading-relaxed">
        Brighter areas indicate pixels re-compressed at a different level —
        a sign they may have been edited or pasted from another source.
      </p>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="bg-raised border border-border px-3 py-2">
      <p className="font-mono text-xs text-muted">{label}</p>
      <p className="font-mono font-medium text-sm text-primary mt-0.5">{value}</p>
    </div>
  )
}
