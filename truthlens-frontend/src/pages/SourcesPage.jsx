/**
 * SourcesPage.jsx
 *
 * CRUD management UI for the trusted_sources PostgreSQL table.
 * Demonstrates SQL knowledge to evaluators.
 *
 * Features:
 *  - Lists all trusted sources with category badges
 *  - Form to add a new source (name, domain, category)
 *  - Delete button per row
 */

import { useState, useEffect } from "react"
import { PlusIcon, Trash2Icon, ShieldCheckIcon } from "lucide-react"
import { getSources, addSource, deleteSource } from "../services/api"

const CATEGORIES = ["news", "fact-check", "government", "academic"]

const CATEGORY_COLORS = {
  "news":        "bg-verified/10 text-verified border-verified/30",
  "fact-check":  "bg-uncertain/10 text-uncertain border-uncertain/30",
  "government":  "bg-ink/10 text-ink border-ink/20",
  "academic":    "bg-flag/10 text-flag border-flag/30",
}

export default function SourcesPage() {
  const [sources, setSources]     = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError]         = useState(null)

  // Form state
  const [name, setName]         = useState("")
  const [domain, setDomain]     = useState("")
  const [category, setCategory] = useState("news")
  const [adding, setAdding]     = useState(false)
  const [formError, setFormError] = useState(null)

  useEffect(() => { fetchSources() }, [])

  async function fetchSources() {
    setIsLoading(true)
    try {
      const data = await getSources()
      setSources(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  async function handleAdd() {
    if (!name.trim() || !domain.trim()) {
      setFormError("Both name and domain are required.")
      return
    }
    setAdding(true)
    setFormError(null)
    try {
      const newSource = await addSource(name.trim(), domain.trim(), category)
      setSources([newSource, ...sources])
      setName("")
      setDomain("")
      setCategory("news")
    } catch (err) {
      setFormError(err.message)
    } finally {
      setAdding(false)
    }
  }

  async function handleDelete(id) {
    try {
      await deleteSource(id)
      setSources(sources.filter((s) => s.id !== id))
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-12 space-y-8">

      <div>
        <p className="data-text text-flag mb-1">DATABASE</p>
        <h1 className="text-3xl font-display font-700">Trusted Sources</h1>
        <p className="text-ink/60 mt-2 text-sm max-w-lg">
          Manage the list of trusted domains used by the text credibility checker
          to verify claims against reliable news sources.
        </p>
      </div>

      {/* Add source form */}
      <div className="border border-line p-5 space-y-4">
        <p className="data-text text-ink/40 text-xs">ADD NEW SOURCE</p>

        <div className="grid md:grid-cols-3 gap-3">
          <div>
            <label className="data-text text-xs text-ink/40 block mb-1">SOURCE NAME</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="BBC News"
              className="w-full border border-line px-3 py-2 text-sm outline-none
                         focus:border-ink transition-colors bg-white"
            />
          </div>
          <div>
            <label className="data-text text-xs text-ink/40 block mb-1">DOMAIN</label>
            <input
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="bbc.com"
              className="w-full border border-line px-3 py-2 text-sm font-mono outline-none
                         focus:border-ink transition-colors bg-white"
            />
          </div>
          <div>
            <label className="data-text text-xs text-ink/40 block mb-1">CATEGORY</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full border border-line px-3 py-2 text-sm outline-none
                         focus:border-ink transition-colors bg-white"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>

        {formError && (
          <p className="text-xs text-flag">{formError}</p>
        )}

        <button
          onClick={handleAdd}
          disabled={adding}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors
                      ${adding ? "bg-ink/40 text-paper cursor-not-allowed" : "bg-ink text-paper hover:bg-ink/90"}`}
        >
          <PlusIcon size={14} />
          {adding ? "Adding…" : "Add Source"}
        </button>
      </div>

      {/* Sources table */}
      {isLoading ? (
        <p className="data-text text-ink/40 text-sm">Loading sources…</p>
      ) : error ? (
        <div className="border border-flag/40 bg-flag/5 px-4 py-3">
          <p className="text-sm text-flag">{error}</p>
          <p className="text-xs text-ink/50 mt-1">
            Make sure the backend is running and DATABASE_URL is set in .env
          </p>
        </div>
      ) : (
        <div className="border border-line divide-y divide-line">
          {/* Table header */}
          <div className="grid grid-cols-12 px-4 py-2 bg-paper">
            <span className="data-text text-xs text-ink/40 col-span-1">#</span>
            <span className="data-text text-xs text-ink/40 col-span-4">NAME</span>
            <span className="data-text text-xs text-ink/40 col-span-4">DOMAIN</span>
            <span className="data-text text-xs text-ink/40 col-span-2">CATEGORY</span>
            <span className="data-text text-xs text-ink/40 col-span-1"></span>
          </div>

          {sources.length === 0 ? (
            <div className="px-4 py-8 text-center">
              <ShieldCheckIcon size={24} className="text-ink/20 mx-auto mb-2" />
              <p className="text-sm text-ink/40">No sources yet. Add one above.</p>
            </div>
          ) : (
            sources.map((source) => (
              <div key={source.id} className="grid grid-cols-12 px-4 py-3 items-center hover:bg-ink/[0.02]">
                <span className="font-mono text-xs text-ink/30 col-span-1">{source.id}</span>
                <span className="text-sm font-medium col-span-4">{source.name}</span>
                <span className="font-mono text-xs text-ink/60 col-span-4">{source.domain}</span>
                <span className="col-span-2">
                  <span className={`text-xs font-mono border px-2 py-0.5 ${CATEGORY_COLORS[source.category] || "bg-line text-ink"}`}>
                    {source.category}
                  </span>
                </span>
                <div className="col-span-1 flex justify-end">
                  <button
                    onClick={() => handleDelete(source.id)}
                    className="text-ink/30 hover:text-flag transition-colors p-1"
                    title="Remove source"
                  >
                    <Trash2Icon size={14} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      <p className="data-text text-xs text-ink/30">
        {sources.length} source{sources.length !== 1 ? "s" : ""} in database
      </p>
    </div>
  )
}
