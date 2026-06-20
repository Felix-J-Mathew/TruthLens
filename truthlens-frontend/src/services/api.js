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

// ── Trusted sources (CRUD) ────────────────────────────────────────────────────

export async function getSources() {
  return handleResponse(await fetch(`${BASE_URL}/api/sources/`))
}

export async function addSource(name, domain, category) {
  return handleResponse(
    await fetch(`${BASE_URL}/api/sources/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, domain, category }),
    })
  )
}

export async function deleteSource(id) {
  return handleResponse(
    await fetch(`${BASE_URL}/api/sources/${id}`, { method: "DELETE" })
  )
}
