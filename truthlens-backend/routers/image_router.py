"""
routers/image_router.py

Defines the HTTP endpoint the React frontend calls when a user uploads
an image. It receives the file, passes it to the image analysis service,
and returns a structured JSON result.

Endpoint:  POST /api/image/analyze
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from services import image_service

router = APIRouter()


@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Receives an uploaded image file from the frontend.

    UploadFile is a FastAPI type that wraps the raw bytes sent in the
    multipart/form-data request.  We read it into memory, then pass
    the raw bytes to the image service which does all the analysis.
    """

    # Guard: only accept image files
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be an image (JPEG, PNG, etc.)"
        )

    # Read the file bytes into memory
    image_bytes = await file.read()

    try:
        result = image_service.run_full_analysis(image_bytes, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result
