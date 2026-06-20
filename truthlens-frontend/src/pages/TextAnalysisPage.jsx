import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { FileTextIcon } from "lucide-react"
import { analyzeText } from "../services/api"
import TextInputBox from "../components/textChecker/TextInputBox"
import CredibilityResultCard from "../components/textChecker/CredibilityResultCard"
import VerdictSummary from "../components/report/VerdictSummary"

export default function TextAnalysisPage() {
  const navigate = useNavigate()
  const [text, setText]           = useState("")
  const [url, setUrl]             = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult]       = useState(null)
  const [error, setError]         = useState(null)

  async function handleSubmit() {
    setIsLoading(true); setError(null)
    try { setResult(await analyzeText(text, url)) }
    catch (err) { setError(err.message) }
    finally { setIsLoading(false) }
  }

  function handleReset() {
    setText(""); setUrl(""); setResult(null); setError(null)
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-12 space-y-8">

      <div>
        <p className="font-mono text-xs text-flag tracking-widest mb-1">MODULE 02</p>
        <h1 className="text-3xl font-display font-bold text-primary">Text Credibility Checker</h1>
        <p className="text-secondary mt-2 text-sm max-w-lg">
          Paste an article or claim to check for sensational language,
          linguistic red flags, and source corroboration.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <TextInputBox
            text={text} onTextChange={setText}
            url={url}   onUrlChange={setUrl}
            onSubmit={handleSubmit} isLoading={isLoading}
          />
          {result && (
            <button onClick={handleReset}
              className="w-full py-2 border border-border text-secondary text-sm
                         hover:border-secondary hover:text-primary transition-colors">
              Check another article
            </button>
          )}
          {error && (
            <div className="border border-flag/30 bg-flag/5 px-4 py-3 space-y-1">
              <p className="text-sm text-flag font-medium">Analysis failed</p>
              <p className="text-xs text-secondary">{error}</p>
              <p className="text-xs text-muted">Make sure the backend is running at localhost:8000</p>
            </div>
          )}
        </div>

        <div className="space-y-3">
          {result ? (
            <>
              <VerdictSummary overall={result.overall} />
              <button
                onClick={() => navigate("/report", { state: { result, type: "text" } })}
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
          <div className="grid md:grid-cols-3 gap-4">

            <CredibilityResultCard title="SIGNAL 01 — SENSATIONALISM" signal={result.signals.sensationalism}>
              {result.signals.sensationalism.matched_phrases.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {result.signals.sensationalism.matched_phrases.map((phrase) => (
                    <span key={phrase}
                      className="px-2 py-0.5 text-xs bg-flag/10 text-flag border border-flag/20 font-mono">
                      {phrase}
                    </span>
                  ))}
                </div>
              )}
            </CredibilityResultCard>

            <CredibilityResultCard title="SIGNAL 02 — LANGUAGE PATTERNS" signal={result.signals.language}>
              {result.signals.language.available && result.signals.language.flags?.length > 0 && (
                <ul className="space-y-1">
                  {result.signals.language.flags.map((flag) => (
                    <li key={flag} className="text-xs text-uncertain flex gap-2">
                      <span>·</span>{flag}
                    </li>
                  ))}
                </ul>
              )}
              {result.signals.language.available && (
                <div className="grid grid-cols-2 gap-2 mt-2">
                  <MiniStat label="Caps ratio"   value={`${Math.round((result.signals.language.cap_ratio||0)*100)}%`} />
                  <MiniStat label="Avg sent len" value={result.signals.language.avg_sentence_length} />
                  <MiniStat label="Entities"     value={result.signals.language.entity_count} />
                  <MiniStat label="Exclamations" value={result.signals.language.exclamation_count} />
                </div>
              )}
            </CredibilityResultCard>

            <CredibilityResultCard title="SIGNAL 03 — SOURCE VERIFICATION" signal={result.signals.source}>
              {result.signals.source.available && result.signals.source.sources_found?.length > 0 && (
                <ul className="space-y-1">
                  {result.signals.source.sources_found.slice(0, 4).map((src) => (
                    <li key={src} className="text-xs text-verified flex gap-2">
                      <span>✓</span>{src}
                    </li>
                  ))}
                </ul>
              )}
              {!result.signals.source.available && (
                <p className="text-xs text-muted italic">
                  Add a NewsAPI key in .env to enable this.
                </p>
              )}
            </CredibilityResultCard>
          </div>

          <div className="bg-surface border border-border px-4 py-3 flex gap-8">
            <MiniStat label="Text length" value={`${result.text_length} chars`} />
            {result.url && <MiniStat label="Source URL" value={result.url} />}
          </div>
        </div>
      )}
    </div>
  )
}

function MiniStat({ label, value }) {
  return (
    <div>
      <p className="font-mono text-xs text-muted">{label}</p>
      <p className="font-mono text-xs text-primary mt-0.5 truncate">{value}</p>
    </div>
  )
}
