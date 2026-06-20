"""
routers/text_router.py

Endpoint:  POST /api/text/analyze
Accepts a JSON body containing the article text (and optional URL),
passes it to the text service, returns credibility signals.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import text_service

router = APIRouter()


# Pydantic model — defines the shape of the JSON body the frontend sends.
# FastAPI validates it automatically; if a required field is missing,
# it returns a 422 error with a helpful message.
class TextAnalysisRequest(BaseModel):
    text: str
    url: str = ""          # optional — if user pastes a URL instead of text


@router.post("/analyze")
async def analyze_text(body: TextAnalysisRequest):
    if len(body.text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least 50 characters of text to analyse."
        )

    try:
        result = text_service.run_full_analysis(body.text, body.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result
