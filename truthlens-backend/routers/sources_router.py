"""
routers/sources_router.py
CRUD endpoints for the trusted_sources table.

GET    /api/sources          → list all sources
POST   /api/sources          → add a source
DELETE /api/sources/{id}     → remove a source
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import sources_service

router = APIRouter()

class SourceCreate(BaseModel):
    name: str
    domain: str
    category: str = "news"   # news | fact-check | government | academic

@router.get("/")
def list_sources():
    return sources_service.get_all()

@router.post("/")
def add_source(body: SourceCreate):
    if not body.name.strip() or not body.domain.strip():
        raise HTTPException(status_code=400, detail="Name and domain are required.")
    return sources_service.create(body.name.strip(), body.domain.strip(), body.category)

@router.delete("/{source_id}")
def remove_source(source_id: int):
    deleted = sources_service.delete(source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found.")
    return {"deleted": source_id}
