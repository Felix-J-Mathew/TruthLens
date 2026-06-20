import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { ScanIcon, RotateCcwIcon, AlertTriangleIcon, FileTextIcon } from "lucide-react"
import { analyzeImage } from "../services/api"
import UploadBox from "../components/imageForensics/UploadBox"
import ELAHeatmapView from "../components/imageForensics/ELAHeatmapView"
import MetadataPanel from "../components/imageForensics/MetadataPanel"
import CloneDetectionView from "../components/imageForensics/CloneDetectionView"
import VerdictSummary from "../components/report/VerdictSummary"

export default function ImageAnalysisPage() {
  const navigate = useNavigate()
  const [file, setFile]           = useState(null)
  const [preview, setPreview]     = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult]       = useState(null)
  const [error, setError]         = useState(null)

  function handleFileSelected(f) {
    setFile(f); setResult(null); setError(null)
    setPreview(URL.createObjectURL(f))
  }

  async function handleAnalyze() {
    if (!file) return
    setIsLoading(true); setError(null)
    try { setResult(await analyzeImage(file)) }
    catch (err) { setError(err.message) }
    finally { setIsLoading(false) }
  }

  function handleReset() {
    setFile(null); setPreview(null); setResult(null); setError(null)
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-12 space-y-8">

      <div>
        <p className="font-mono text-xs text-flag tracking-widest mb-1">MODULE 01</p>
        <h1 className="text-3xl font-display font-bold text-primary">Image Forensics</h1>
        <p className="text-secondary mt-2 text-sm max-w-lg">
          Upload an image to run ELA, metadata inspection, noise analysis,
          frequency analysis, and clone detection.
        </p>
      </div>

      {result?.signals?.screenshot?.is_screenshot && (
        <div className="flex gap-3 items-start border border-uncertain/30 bg-uncertain/5 px-4 py-3">
          <AlertTriangleIcon size={15} className="text-uncertain mt-0.5 shrink-0" />
          <p className="text-sm text-uncertain">
            This appears to be a screenshot. Forensic signals may be less reliable.
          </p>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        {/* Left: upload */}
        <div className="space-y-4">
          {!preview ? (
            <UploadBox onFileSelected={handleFileSelected} isLoading={isLoading} />
          ) : (
            <div className="space-y-3">
              <div className="specimen-frame border border-border bg-black flex items-center justify-center">
                <img src={preview} alt="Selected" className="max-h-72 w-full object-contain" />
              </div>
              <p className="font-mono text-xs text-muted truncate">{file?.name}</p>
              <div className="flex gap-3">
                <button onClick={handleAnalyze} disabled={isLoading}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5
                              font-medium text-sm transition-colors rounded-sm
                              ${isLoading
                                ? "bg-accent/40 text-white cursor-not-allowed"
                                : "bg-accent text-white hover:bg-accent/90"}`}>
                  <ScanIcon size={14} />
                  {isLoading ? "Running analysis…" : "Run Forensics"}
                </button>
                <button onClick={handleReset} disabled={isLoading}
                  className="px-3 py-2.5 border border-border hover:border-secondary
                             transition-colors text-secondary">
                  <RotateCcwIcon size={14} />
                </button>
              </div>
            </div>
          )}

          {isLoading && (
            <div className="bg-surface border border-border p-4 space-y-2">
              <p className="font-mono text-xs text-muted">RUNNING SIGNALS</p>
              {["ELA", "Metadata", "Noise Analysis", "Frequency", "Clone Detection"].map((s) => (
                <div key={s} className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-accent rounded-full animate-pulse" />
                  <span className="text-xs text-secondary">{s}</span>
                </div>
              ))}
            </div>
          )}

          {error && (
            <div className="border border-flag/30 bg-flag/5 px-4 py-3 space-y-1">
              <p className="text-sm text-flag font-medium">Analysis failed</p>
              <p className="text-xs text-secondary">{error}</p>
              <p className="text-xs text-muted">Make sure the backend is running at localhost:8000</p>
            </div>
          )}
        </div>

        {/* Right: verdict */}
        <div className="space-y-3">
          {result ? (
            <>
              <VerdictSummary overall={result.overall} filename={result.filename} />
              <button
                onClick={() => navigate("/report", { state: { result, type: "image" } })}
                className="w-full flex items-center justify-center gap-2 py-2.5 border
                           border-border text-secondary text-sm font-medium
                           hover:border-accent hover:text-accent transition-colors">
                <FileTextIcon size={13} /> View Full Report
              </button>
            </>
          ) : (
            <div className="border border-dashed border-border bg-surface p-8
                            flex items-center justify-center h-full min-h-48">
              <p className="font-mono text-xs text-muted text-center">
                Verdict appears here after analysis
              </p>
            </div>
          )}
        </div>
      </div>

      {result && (
        <div className="space-y-4 pt-6 border-t border-border">
          <p className="font-mono text-xs text-muted tracking-widest">SIGNAL BREAKDOWN</p>
          <div className="grid md:grid-cols-2 gap-4">
            <ELAHeatmapView ela={result.signals.ela} />
            <MetadataPanel  metadata={result.signals.metadata} />
            <CloneDetectionView    clone={result.signals.clone} />
          </div>

          {/* Noise card */}
          <div className="bg-surface border border-border p-5 space-y-3">
            <p className="font-mono text-xs text-muted">SIGNAL 05 — NOISE CONSISTENCY</p>
            <p className="font-medium text-primary text-sm">{result.signals.noise.verdict}</p>
            <div className="flex gap-6">
              {[
                ["Mean Noise",     result.signals.noise.mean_noise_level],
                ["Block Variance", result.signals.noise.between_block_variance],
                ["Suspicion",      `${result.signals.noise.suspicion_score} / 100`],
              ].map(([label, val]) => (
                <div key={label}>
                  <p className="font-mono text-xs text-muted">{label}</p>
                  <p className="font-mono text-sm text-primary mt-0.5">{val}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
