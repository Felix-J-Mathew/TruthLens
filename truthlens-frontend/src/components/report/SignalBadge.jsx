export default function SignalBadge({ score }) {
  let colorClass, label
  if (score <= 30) {
    colorClass = "bg-verified/10 text-verified border-verified/20"
    label = "Low Risk"
  } else if (score <= 60) {
    colorClass = "bg-uncertain/10 text-uncertain border-uncertain/20"
    label = "Uncertain"
  } else {
    colorClass = "bg-flag/10 text-flag border-flag/20"
    label = "Suspicious"
  }
  return (
    <div className={`shrink-0 border px-2.5 py-1 text-xs font-mono font-medium ${colorClass}`}>
      {score} · {label}
    </div>
  )
}
