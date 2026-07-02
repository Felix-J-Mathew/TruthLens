/**
 * services/api.js
 * All fetch calls to the FastAPI backend live here.
 */

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

async function handleResponse(res) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }))
    throw new Error(err.detail || "Request failed")
  }
  return res.json()
}

// ── Image forensics ───────────────────────────────────────────────────────────

export async function analyzeImage(file) {
  const formData = new FormData()
  formData.append("file", file)
  return handleResponse(
    await fetch(`${BASE_URL}/api/image/analyze`, { method: "POST", body: formData })
  )
}

// ── Text credibility ──────────────────────────────────────────────────────────

export async function analyzeText(text, url = "") {
  return handleResponse(
    await fetch(`${BASE_URL}/api/text/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, url }),
    })
  )
}


