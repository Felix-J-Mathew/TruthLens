import { SearchIcon } from "lucide-react"

export default function TextInputBox({ text, onTextChange, url, onUrlChange, onSubmit, isLoading }) {
  const canSubmit = text.trim().length >= 50 && !isLoading
  return (
    <div className="space-y-3">
      <div>
        <label className="font-mono text-xs text-muted block mb-1.5">
          ARTICLE TEXT — minimum 50 characters
        </label>
        <textarea
          value={text}
          onChange={(e) => onTextChange(e.target.value)}
          placeholder="Paste the article, headline, or claim you want to check…"
          rows={8}
          className="w-full border border-border bg-raised text-primary text-sm
                     p-4 resize-y outline-none focus:border-accent transition-colors
                     placeholder:text-muted font-body"
          disabled={isLoading}
        />
        <p className="font-mono text-xs text-muted mt-1 text-right">
          {text.length} characters
        </p>
      </div>

      <div>
        <label className="font-mono text-xs text-muted block mb-1.5">SOURCE URL — optional</label>
        <input
          type="url"
          value={url}
          onChange={(e) => onUrlChange(e.target.value)}
          placeholder="https://example.com/article"
          className="w-full border border-border bg-raised font-mono text-sm text-primary
                     px-4 py-2.5 outline-none focus:border-accent transition-colors
                     placeholder:text-muted"
          disabled={isLoading}
        />
      </div>

      <button
        onClick={onSubmit}
        disabled={!canSubmit}
        className={`w-full flex items-center justify-center gap-2 py-3 font-medium text-sm
                    transition-colors rounded-sm
                    ${canSubmit
                      ? "bg-accent text-white hover:bg-accent/90"
                      : "bg-raised text-muted cursor-not-allowed border border-border"
                    }`}
      >
        <SearchIcon size={14} />
        {isLoading ? "Analysing…" : "Analyse Text"}
      </button>

      {text.length > 0 && text.length < 50 && (
        <p className="text-xs text-uncertain font-mono">
          Need {50 - text.length} more characters.
        </p>
      )}
    </div>
  )
}
