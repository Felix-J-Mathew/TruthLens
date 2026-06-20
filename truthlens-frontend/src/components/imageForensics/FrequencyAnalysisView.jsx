import SignalBadge from "../report/SignalBadge"

export default function FrequencyAnalysisView({ frequency }) {
  const total = frequency.low_freq_energy + frequency.high_freq_energy + 0.0001
  const lowPct  = Math.round((frequency.low_freq_energy / total) * 100)
  const highPct = 100 - lowPct

  return (
    <div className="bg-surface border border-border p-5 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs text-muted mb-1">SIGNAL 03 — FREQUENCY ANALYSIS</p>
          <p className="font-medium text-primary text-sm">{frequency.verdict}</p>
        </div>
        <SignalBadge score={frequency.suspicion_score} />
      </div>

      <div>
        <p className="font-mono text-xs text-muted mb-2">FREQUENCY DISTRIBUTION</p>
        <div className="flex h-5 w-full overflow-hidden border border-border rounded-sm">
          <div className="bg-verified/70 flex items-center justify-center text-white text-xs font-mono"
               style={{ width: `${lowPct}%` }}>
            {lowPct > 20 ? `${lowPct}%` : ""}
          </div>
          <div className="bg-flag/60 flex items-center justify-center text-white text-xs font-mono"
               style={{ width: `${highPct}%` }}>
            {highPct > 20 ? `${highPct}%` : ""}
          </div>
        </div>
        <div className="flex justify-between font-mono text-xs text-muted mt-1">
          <span>Low freq (natural)</span>
          <span>High freq (artefacts)</span>
        </div>
      </div>

      <p className="text-xs text-secondary leading-relaxed">
        AI-generated images show an unnaturally high ratio of high-frequency
        energy caused by repeating convolutional patterns in neural networks.
      </p>
    </div>
  )
}
