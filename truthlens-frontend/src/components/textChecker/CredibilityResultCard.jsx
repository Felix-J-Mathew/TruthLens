import SignalBadge from "../report/SignalBadge"

export default function CredibilityResultCard({ title, signal, children }) {
  return (
    <div className="bg-surface border border-border p-5 space-y-3">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs text-muted mb-1">{title}</p>
          <p className="font-medium text-primary text-sm">{signal.verdict}</p>
        </div>
        <SignalBadge score={signal.suspicion_score} />
      </div>
      {children}
    </div>
  )
}
