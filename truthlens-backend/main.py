import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from routers import image_router, text_router, sources_router

load_dotenv()

app = FastAPI(title="TruthLens API", version="0.1.0")

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://truth-lens-phi.vercel.app/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "https://truth-lens-phi.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_router.router,   prefix="/api/image",   tags=["Image Forensics"])
app.include_router(text_router.router,    prefix="/api/text",    tags=["Text Credibility"])
app.include_router(sources_router.router, prefix="/api/sources", tags=["Trusted Sources"])

@app.get("/")
def health_check():
    return {"status": "TruthLens API is running"}
