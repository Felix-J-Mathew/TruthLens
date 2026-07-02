/**
 * ReportPage.jsx
 *
 * Displays a full per-analysis report. The result data is passed via
 * React Router location state so no extra API call is needed.
 *
 * To navigate here from ImageAnalysisPage or TextAnalysisPage:
 *   navigate("/report", { state: { result, type: "image" | "text" } })
 *
 * If someone lands here directly (no state), we show a "no report" message.
 */

import { useLocation, useNavigate } from "react-router-dom"
import { ArrowLeftIcon, PrinterIcon } from "lucide-react"
import VerdictSummary from "../components/report/VerdictSummary"
import SignalBadge from "../components/report/SignalBadge"

export default function ReportPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state

  if (!state?.result) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-16 text-center">
        <p className="data-text text-ink/40 mb-3">NO REPORT LOADED</p>
        <p className="text-ink/60 mb-6 text-sm">
          Run an analysis first, then view the full report from the results page.
        </p>
        <button
          onClick={() => navigate("/")}
          className="px-5 py-2.5 bg-ink text-paper text-sm font-medium hover:bg-ink/90 transition-colors"
        >
          Go to Home
        </button>
      </div>
    )
  }

  const { result, type } = state
  const isImage = type === "image"

  return (
    <div className="max-w-5xl mx-auto px-6 py-12 space-y-8">

      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-sm text-ink/60 hover:text-ink transition-colors"
        >
          <ArrowLeftIcon size={15} /> Back to analysis
        </button>
        <button
          onClick={() => window.print()}
          className="flex items-center gap-2 text-sm border border-line px-3 py-1.5
                     hover:border-ink transition-colors"
        >
          <PrinterIcon size={14} /> Print / Save PDF
        </button>
      </div>

      {/* Header */}
      <div>
        <p className="data-text text-flag mb-1">
          {isImage ? "IMAGE FORENSICS REPORT" : "TEXT CREDIBILITY REPORT"}
        </p>
        <h1 className="text-3xl font-display font-700">
          {isImage ? result.filename : "Article Analysis"}
        </h1>
        {isImage && (
          <p className="data-text text-ink/40 text-xs mt-1">
            {result.image_size?.width} × {result.image_size?.height} px
          </p>
        )}
      </div>

      {/* Overall verdict */}
      <VerdictSummary overall={result.overall} filename={isImage ? result.filename : null} />

      {/* Signal table */}
      <div className="space-y-3">
        <p className="data-text text-ink/40 text-xs">SIGNAL-BY-SIGNAL BREAKDOWN</p>

        {isImage ? (
          <ImageSignalTable signals={result.signals} />
        ) : (
          <TextSignalTable signals={result.signals} />
        )}
      </div>

      {/* ELA heatmap in report (image only) */}
      {isImage && result.signals?.ela?.heatmap_base64 && (
        <div className="space-y-2">
          <p className="data-text text-ink/40 text-xs">ELA HEATMAP</p>
          <div className="specimen-frame border border-line bg-black">
            <img
              src={`data:image/png;base64,${result.signals.ela.heatmap_base64}`}
              alt="ELA heatmap"
              className="w-full object-contain max-h-96"
            />
          </div>
        </div>
      )}

      {/* GPS if present */}
      {isImage && result.signals?.metadata?.gps && (
        <div className="border border-line p-4 space-y-1">
          <p className="data-text text-xs text-ink/40">GPS COORDINATES EXTRACTED</p>
          <p className="font-mono text-sm">
            {result.signals.metadata.gps.latitude}, {result.signals.metadata.gps.longitude}
          </p>
          <a
            href={`https://maps.google.com/?q=${result.signals.metadata.gps.latitude},${result.signals.metadata.gps.longitude}`}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-verified underline"
          >
            View on Google Maps ↗
          </a>
        </div>
      )}

      <p className="data-text text-xs text-ink/30 pt-4 border-t border-line">
        TruthLens · Analysis generated {new Date().toLocaleString()} ·
        Results are probabilistic, not conclusive. Always verify with primary sources.
      </p>
    </div>
  )
}

// ── Image signal summary table ────────────────────────────────────────────────

function ImageSignalTable({ signals }) {
  const rows = [
    { label: "Screenshot Check",      verdict: signals.screenshot?.verdict,  score: signals.screenshot?.is_screenshot ? 60 : 0 },
    { label: "Error Level Analysis",  verdict: signals.ela?.verdict,         score: signals.ela?.suspicion_score },
    { label: "Metadata Inspection",   verdict: signals.metadata?.verdict,    score: { low:10, medium:40, high:80, unknown:30 }[signals.metadata?.risk_level] ?? 30 },
    { label: "Noise Consistency",     verdict: signals.noise?.verdict,       score: signals.noise?.suspicion_score },
  ]
  return <SignalTable rows={rows} />
}

// ── Text signal summary table ─────────────────────────────────────────────────

function TextSignalTable({ signals }) {
  const rows = [
    { label: "Sensationalism",       verdict: signals.sensationalism?.verdict, score: signals.sensationalism?.suspicion_score },
    { label: "Language Patterns",    verdict: signals.language?.verdict,       score: signals.language?.suspicion_score },
    { label: "Source Verification",  verdict: signals.source?.verdict,         score: signals.source?.suspicion_score },
  ]
  return <SignalTable rows={rows} />
}

function SignalTable({ rows }) {
  return (
    <div className="border border-line divide-y divide-line">
      {rows.map((row) => (
        <div key={row.label} className="flex items-center gap-4 px-4 py-3">
          <span className="data-text text-xs text-ink/50 w-44 shrink-0">{row.label}</span>
          <span className="text-sm text-ink flex-1">{row.verdict}</span>
          <SignalBadge score={row.score ?? 0} />
        </div>
      ))}
    </div>
  )
}