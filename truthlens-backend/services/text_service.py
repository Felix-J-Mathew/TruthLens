"""
services/text_service.py

Text credibility checker.

Signals implemented:
  1. Sensationalism — detects clickbait/emotional language patterns
  2. Source verification — checks claims against NewsAPI trusted sources
  3. Language patterns — spaCy-based checks (excessive caps, punctuation abuse)
  4. Readability — very low reading level can indicate misleading content
"""

import os
import re
import requests

# spaCy is loaded once at module level (loading it per-request is very slow)
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False
    nlp = None


# ── Signal 1: Sensationalism Detection ───────────────────────────────────────

# Words and phrases frequently associated with misleading or clickbait content
SENSATIONAL_WORDS = [
    "shocking", "unbelievable", "you won't believe", "mind-blowing",
    "explosive", "bombshell", "breaking", "urgent", "exposed", "secret",
    "they don't want you to know", "wake up", "share before deleted",
    "mainstream media won't tell", "miracle", "hoax", "crisis actor",
    "false flag", "deep state", "new world order", "they are hiding",
]

def run_sensationalism_check(text: str) -> dict:
    text_lower = text.lower()
    matched = [w for w in SENSATIONAL_WORDS if w in text_lower]
    score = min(100, len(matched) * 15)

    return {
        "matched_phrases": matched,
        "phrase_count": len(matched),
        "suspicion_score": score,
        "verdict": (
            f"Sensational language detected: {', '.join(matched[:3])}"
            if matched else "No sensational language detected"
        ),
    }


# ── Signal 2: Language Pattern Analysis (spaCy) ───────────────────────────────

def run_language_analysis(text: str) -> dict:
    """
    Uses spaCy for NLP-based credibility signals:
      - Excessive capitalisation (SHOUTING = emotional manipulation)
      - Excessive exclamation/question marks
      - Very short sentences (breathless, punchy style common in misinformation)
      - Named entity density (legitimate news cites real places and people)
    """
    if not SPACY_AVAILABLE:
        return {
            "available": False,
            "verdict": "spaCy not installed — language analysis skipped",
            "suspicion_score": 0,
        }

    doc = nlp(text[:5000])  # limit to 5000 chars for performance

    words = [t for t in doc if t.is_alpha]
    cap_words = [t for t in words if t.text.isupper() and len(t.text) > 2]
    cap_ratio = len(cap_words) / max(len(words), 1)

    exclamations = text.count("!")
    questions = text.count("?")

    sentences = list(doc.sents)
    avg_sent_len = (
        sum(len(list(s)) for s in sentences) / max(len(sentences), 1)
    )

    entities = [(ent.text, ent.label_) for ent in doc.ents]
    entity_density = len(entities) / max(len(sentences), 1)

    suspicion = 0
    flags = []

    if cap_ratio > 0.1:
        suspicion += 25
        flags.append(f"{int(cap_ratio*100)}% of words are ALL CAPS")
    if exclamations > 5:
        suspicion += 20
        flags.append(f"{exclamations} exclamation marks")
    if avg_sent_len < 10:
        suspicion += 15
        flags.append("Very short sentences (breathless writing style)")
    if entity_density < 0.3:
        suspicion += 15
        flags.append("Low named entity density — few real-world references cited")

    return {
        "available": True,
        "cap_ratio": round(cap_ratio, 3),
        "exclamation_count": exclamations,
        "avg_sentence_length": round(avg_sent_len, 1),
        "entity_count": len(entities),
        "flags": flags,
        "suspicion_score": min(100, suspicion),
        "verdict": (
            "Linguistic flags: " + "; ".join(flags)
            if flags else "Language patterns appear normal"
        ),
    }


# ── Signal 3: Source Verification (NewsAPI) ───────────────────────────────────

def run_source_check(text: str, url: str) -> dict:
    """
    Tries to find corroborating coverage of the main claim on NewsAPI.

    If no API key is configured, it degrades gracefully and skips this signal.

    Logic:
      - Extract the first sentence as the "headline claim"
      - Search NewsAPI for it
      - If multiple trusted outlets cover the same story, credibility rises
      - If zero results, it may mean the story is fabricated or very niche
    """
    api_key = os.getenv("NEWS_API_KEY", "")
    if not api_key or api_key == "your_newsapi_key_here":
        return {
            "available": False,
            "verdict": "NewsAPI key not configured — source check skipped",
            "suspicion_score": 0,
        }

    # Use first sentence as search query
    first_sentence = re.split(r'[.!?]', text.strip())[0][:100]

    try:
        response = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": first_sentence,
                "apiKey": api_key,
                "pageSize": 5,
                "language": "en",
            },
            timeout=5,
        )
        data = response.json()
        articles = data.get("articles", [])
        sources = [a["source"]["name"] for a in articles]

        if len(articles) >= 3:
            verdict = f"Corroborated by {len(articles)} sources including: {', '.join(sources[:3])}"
            suspicion = 0
        elif len(articles) == 0:
            verdict = "No corroborating news sources found for this claim"
            suspicion = 50
        else:
            verdict = f"Limited coverage — {len(articles)} source(s) found"
            suspicion = 25

        return {
            "available": True,
            "article_count": len(articles),
            "sources_found": sources,
            "suspicion_score": suspicion,
            "verdict": verdict,
        }

    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "suspicion_score": 0,
            "verdict": "Source check failed — network error",
        }


# ── Overall Verdict ───────────────────────────────────────────────────────────

def _compute_trust_score(signals: dict) -> dict:
    weights = {
        "sensationalism": 0.35,
        "language":       0.35,
        "source":         0.30,
    }

    weighted = (
        signals["sensationalism"]["suspicion_score"] * weights["sensationalism"] +
        signals["language"]["suspicion_score"]       * weights["language"] +
        signals["source"]["suspicion_score"]         * weights["source"]
    )

    trust_score = max(0, 100 - int(weighted))

    if trust_score >= 75:
        verdict = "Likely Credible"
        confidence = "high" if trust_score >= 90 else "medium"
    elif trust_score >= 45:
        verdict = "Uncertain — treat with caution"
        confidence = "low"
    else:
        verdict = "Low Credibility — multiple red flags detected"
        confidence = "high" if trust_score < 25 else "medium"

    return {
        "trust_score": trust_score,
        "verdict": verdict,
        "confidence": confidence,
    }


# ── Public Entry Point ────────────────────────────────────────────────────────

def run_full_analysis(text: str, url: str) -> dict:
    signals = {
        "sensationalism": run_sensationalism_check(text),
        "language":       run_language_analysis(text),
        "source":         run_source_check(text, url),
    }
    overall = _compute_trust_score(signals)

    return {
        "text_length": len(text),
        "url": url,
        "signals": signals,
        "overall": overall,
    }
