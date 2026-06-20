"""
utils/validators.py

Small reusable helper functions for input validation.
"""

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE_MB = 10


def validate_image_upload(content_type: str, size_bytes: int) -> str | None:
    """
    Returns an error message string if the upload is invalid,
    or None if it's OK.
    """
    if content_type not in ALLOWED_IMAGE_TYPES:
        return f"Unsupported file type: {content_type}. Please upload a JPEG, PNG, or WebP."
    if size_bytes > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        return f"File too large. Maximum size is {MAX_IMAGE_SIZE_MB}MB."
    return None
