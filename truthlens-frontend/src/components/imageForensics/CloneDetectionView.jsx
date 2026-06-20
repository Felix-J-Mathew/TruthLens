import { CopyIcon } from "lucide-react"
import SignalBadge from "../report/SignalBadge"

export default function CloneDetectionView({ clone }) {
  const hasClones = clone.clone_pairs && clone.clone_pairs.length > 0
  return (
    <div className="bg-surface border border-border p-5 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs text-muted mb-1">SIGNAL 04 — CLONE DETECTION</p>
          <p className="font-medium text-primary text-sm">{clone.verdict}</p>
        </div>
        <SignalBadge score={clone.suspicion_score} />
      </div>

      {hasClones ? (
        <div className="space-y-2">
          {clone.clone_pairs.map((pair, i) => (
            <div key={i} className="flex items-center gap-3 px-3 py-2 border border-flag/20 bg-flag/5">
              <CopyIcon size={12} className="text-flag shrink-0" />
              <span className="font-mono text-xs text-secondary">
                [{pair.source[0]}, {pair.source[1]}]
                <span className="text-muted mx-2">→</span>
                [{pair.clone[0]}, {pair.clone[1]}]
              </span>
            </div>
          ))}
        </div>
      ) : (
        <div className="px-3 py-2 border border-verified/20 bg-verified/5">
          <p className="text-sm text-verified font-medium">No matching regions found</p>
        </div>
      )}

      <p className="text-xs text-secondary leading-relaxed">
        Detects copy-pasted regions within the image that may indicate
        content was hidden or replaced.
      </p>
    </div>
  )
}
