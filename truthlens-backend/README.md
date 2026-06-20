# TruthLens Backend

FastAPI backend for the TruthLens media authenticity platform.

## Setup (do this once)

```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download the spaCy language model (needed for text analysis)
python -m spacy download en_core_web_sm

# 5. Copy the environment file and edit it
cp .env.example .env
```

## Running the server

```bash
source venv/bin/activate
uvicorn main:app --reload
```

Server runs at: http://localhost:8000
API docs (auto-generated): http://localhost:8000/docs

## Endpoints

| Method | URL | What it does |
|--------|-----|--------------|
| GET  | / | Health check |
| POST | /api/image/analyze | Image forensics (multipart/form-data) |
| POST | /api/text/analyze  | Text credibility (JSON body) |

## Project structure

```
truthlens-backend/
├── main.py               # FastAPI app, CORS, router registration
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
├── routers/
│   ├── image_router.py   # POST /api/image/analyze
│   └── text_router.py    # POST /api/text/analyze
├── services/
│   ├── image_service.py  # ELA, metadata, noise, frequency, clone detection
│   └── text_service.py   # Sensationalism, language analysis, source check
└── utils/
    └── validators.py     # Input validation helpers
```
