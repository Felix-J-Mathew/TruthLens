import { MapPinIcon, ClockIcon, MonitorIcon, AlertTriangleIcon } from "lucide-react"
import SignalBadge from "../report/SignalBadge"

const RISK_SCORE = { low: 10, medium: 40, high: 80, unknown: 30 }

export default function MetadataPanel({ metadata }) {
  const suspicion = RISK_SCORE[metadata.risk_level] ?? 30
  return (
    <div className="bg-surface border border-border p-5 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs text-muted mb-1">SIGNAL 02 — METADATA INSPECTION</p>
          <p className="font-medium text-primary text-sm">{metadata.verdict}</p>
        </div>
        <SignalBadge score={suspicion} />
      </div>

      {!metadata.has_metadata ? (
        <p className="text-sm text-secondary italic">No EXIF data found in this file.</p>
      ) : (
        <div className="space-y-2">
          {metadata.software && (
            <MetaRow icon={<MonitorIcon size={13} />} label="Software"
              value={metadata.software} highlight={metadata.software_risk} />
          )}
          {metadata.time_gap_hours !== null && (
            <MetaRow icon={<ClockIcon size={13} />} label="Capture → Modified"
              value={`${metadata.time_gap_hours}h gap`} highlight={metadata.time_gap_hours > 24} />
          )}
          {metadata.gps && (
            <MetaRow icon={<MapPinIcon size={13} />} label="GPS"
              value={`${metadata.gps.latitude}, ${metadata.gps.longitude}`} />
          )}
        </div>
      )}
    </div>
  )
}

function MetaRow({ icon, label, value, highlight }) {
  return (
    <div className={`flex items-center gap-3 px-3 py-2 border rounded-sm
      ${highlight ? "border-flag/30 bg-flag/5" : "border-border bg-raised"}`}>
      <span className={highlight ? "text-flag" : "text-muted"}>{icon}</span>
      <span className="font-mono text-xs text-secondary w-32 shrink-0">{label}</span>
      <span className={`font-mono text-xs flex-1 ${highlight ? "text-flag font-medium" : "text-primary"}`}>
        {value}
      </span>
      {highlight && <AlertTriangleIcon size={12} className="text-flag shrink-0" />}
    </div>
  )
}
