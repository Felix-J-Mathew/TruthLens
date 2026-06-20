"""
services/ela_service.py — Error Level Analysis

HOW ELA WORKS (conceptually):
  JPEG is a "lossy" format — every time you save a JPEG, it loses a little
  quality uniformly across unedited areas. If someone pastes or edits a
  region of an image, that region has a different compression history.

  ELA exploits this by:
    1. Re-saving the image at a known quality (e.g. 95%)
    2. Computing the pixel-by-pixel difference between original and re-save
    3. Brightening that difference image so anomalies are visible

  Edited regions show up brighter because they respond differently to
  re-compression than the surrounding unedited pixels.

WHAT WE RETURN:
  - ela_image_base64: the heatmap image encoded as a base64 string
    (React can display this directly in an <img> tag without needing a file)
  - mean_error: average brightness of the difference image (higher = more anomaly)
  - max_error: peak brightness
  - manipulation_detected: True if mean_error exceeds our threshold
  - note: plain-English explanation of the finding
"""

import io
import base64
import numpy as np
from PIL import Image, ImageChops, ImageEnhance


# Threshold above which mean error suggests manipulation.
# Calibrated conservatively — real unedited JPEGs typically score below 8.
ELA_THRESHOLD = 8.0
RESAVE_QUALITY = 95


def run_ela(image_bytes: bytes) -> dict:
    """
    Runs Error Level Analysis on raw image bytes.
    Returns a dict of findings including a base64-encoded heatmap.
    """

    # ── Step 1: Open original image ───────────────────────────────────────────
    original = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # ── Step 2: Re-save at known quality into memory ──────────────────────────
    # We write to a BytesIO buffer instead of disk — faster and no temp files.
    buffer = io.BytesIO()
    original.save(buffer, format="JPEG", quality=RESAVE_QUALITY)
    buffer.seek(0)  # Rewind to the start before reading back
    resaved = Image.open(buffer).convert("RGB")

    # ── Step 3: Compute pixel difference ─────────────────────────────────────
    # ImageChops.difference() subtracts pixel values and takes the absolute value.
    # Result is a grayscale-range image where bright = large difference.
    diff = ImageChops.difference(original, resaved)

    # ── Step 4: Amplify brightness so subtle differences are visible ──────────
    # A scale factor of 20 is standard for ELA visualization.
    enhancer = ImageEnhance.Brightness(diff)
    ela_image = enhancer.enhance(20)

    # ── Step 5: Compute statistics from the difference array ──────────────────
    diff_array = np.array(diff, dtype=np.float32)
    mean_error = float(np.mean(diff_array))
    max_error = float(np.max(diff_array))

    # ── Step 6: Encode heatmap as base64 so React can display it ─────────────
    # React can't receive raw image files in JSON — we encode it as a base64
    # string. React then uses it like: <img src={`data:image/jpeg;base64,${ela_image_base64}`} />
    out_buffer = io.BytesIO()
    ela_image.save(out_buffer, format="JPEG")
    ela_b64 = base64.b64encode(out_buffer.getvalue()).decode("utf-8")

    # ── Step 7: Interpret result ──────────────────────────────────────────────
    manipulation_detected = mean_error > ELA_THRESHOLD

    if mean_error < 4:
        note = "ELA shows uniform error levels across the image — consistent with an unedited photograph."
    elif mean_error < ELA_THRESHOLD:
        note = "ELA shows slightly elevated error levels. Could indicate minor editing or high-quality original."
    else:
        note = "ELA shows uneven error distribution. Certain regions respond differently to re-compression, suggesting possible manipulation."

    return {
        "ela_image_base64": ela_b64,
        "mean_error": round(mean_error, 3),
        "max_error": round(max_error, 3),
        "threshold_used": ELA_THRESHOLD,
        "manipulation_detected": manipulation_detected,
        "note": note,
    }
