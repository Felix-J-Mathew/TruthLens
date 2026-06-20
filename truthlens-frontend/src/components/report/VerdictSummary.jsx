export default function VerdictSummary({ overall, filename }) {
  const { trust_score, verdict, confidence } = overall

  let accent, borderColor, glowClass
  if (trust_score >= 75) {
    accent = "text-verified"
    borderColor = "border-verified/40"
    glowClass = "bg-verified"
  } else if (trust_score >= 45) {
    accent = "text-uncertain"
    borderColor = "border-uncertain/40"
    glowClass = "bg-uncertain"
  } else {
    accent = "text-flag"
    borderColor = "border-flag/40"
    glowClass = "bg-flag"
  }

  return (
    <div className={`border ${borderColor} bg-surface p-6`}>
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          {filename && (
            <p className="font-mono text-xs text-muted mb-2 w-full overflow-hidden"
               style={{ wordBreak: "break-all" }}>
              {filename}
            </p>
          )}
          <h2 className={`text-2xl font-display font-bold ${accent} leading-tight`}>
            {verdict}
          </h2>
          <p className="text-sm text-secondary mt-2">
            Confidence —{" "}
            <span className="text-primary font-medium capitalize">{confidence}</span>
          </p>
        </div>
        <div className="text-right shrink-0">
          <p className={`text-5xl font-display font-bold ${accent}`}>{trust_score}</p>
          <p className="font-mono text-xs text-muted mt-1">TRUST / 100</p>
        </div>
      </div>

      <div className="mt-5 h-1 w-full bg-raised rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-700 ${glowClass}`}
          style={{ width: `${trust_score}%` }}
        />
      </div>
    </div>
  )
}