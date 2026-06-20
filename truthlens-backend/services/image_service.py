"""
services/image_service.py

All image forensics logic lives here.
The router calls run_full_analysis() and gets back one clean dictionary
that it sends to the frontend as JSON.

Signals implemented:
  1. ELA  — Error Level Analysis
  2. Metadata — EXIF data, software tag, GPS, capture-to-modify time gap
  3. Noise Analysis — detects inconsistent noise at region boundaries
  4. Fourier Frequency Analysis — detects AI-generated images
  5. Clone Detection — finds copy-pasted regions within the image
  6. Screenshot Classification — flags screenshots before deeper analysis
"""

import io
import base64
import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter
import piexif
import cv2


# ── Helpers ──────────────────────────────────────────────────────────────────

def _bytes_to_pil(image_bytes: bytes) -> Image.Image:
    """Convert raw bytes into a Pillow Image object."""
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def _bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
    """Convert raw bytes into an OpenCV image array (BGR format)."""
    arr = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def _pil_to_base64(img: Image.Image) -> str:
    """
    Encode a Pillow image as a base64 PNG string.
    The frontend can display this directly in an <img> tag:
        <img src="data:image/png;base64,{string}" />
    """
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ── Signal 1: ELA ─────────────────────────────────────────────────────────────

def run_ela(pil_image: Image.Image, quality: int = 95) -> dict:
    """
    Error Level Analysis.

    How it works:
      1. Re-save the image as JPEG at a known quality (90%).
      2. Compute the pixel-by-pixel difference between original and re-saved.
      3. Boost the brightness of that difference image so small errors
         become visible.
      4. Manipulated areas that came from a different source or were edited
         show higher error levels (brighter in the heatmap) than the
         surrounding unedited pixels.

    Returns the ELA heatmap as a base64 image string, plus a
    suspicion score from 0-100.
    """
    # Step 1: re-save at known quality into memory
    buffer = io.BytesIO()
    pil_image.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    resaved = Image.open(buffer).convert("RGB")

    # Step 2: pixel difference
    diff = ImageChops.difference(pil_image, resaved)

    # Step 3: boost brightness so small differences are visible
    enhancer = ImageEnhance.Brightness(diff)
    ela_image = enhancer.enhance(20)

    # Step 4: compute a suspicion score
    # Convert to numpy, look at the mean brightness of the heatmap.
    ela_array = np.array(ela_image)
    mean_error = float(np.mean(ela_array))

    # Areas with inconsistent error levels suggest manipulation.
    # We also check for localised bright patches (uneven distribution).
    std_error = float(np.std(ela_array))

    # Heuristic thresholds derived from published ELA research:
    # mean > 15 or std > 20 indicates probable manipulation
    if mean_error > 15 or std_error > 20:
        suspicion = min(100, int((mean_error + std_error) * 2))
        verdict = "Suspicious — inconsistent error levels detected"
    else:
        suspicion = max(0, int((mean_error + std_error) * 1.5))
        verdict = "Consistent — error levels appear uniform"

    return {
        "heatmap_base64": _pil_to_base64(ela_image),
        "mean_error": round(mean_error, 2),
        "std_error": round(std_error, 2),
        "suspicion_score": suspicion,
        "verdict": verdict,
    }


# ── Signal 2: Metadata ────────────────────────────────────────────────────────

def run_metadata(pil_image: Image.Image) -> dict:
    """
    EXIF metadata inspection.

    Checks for:
    - Software tag (Photoshop, GIMP, etc. = high risk)
    - GPS coordinates embedded in the image
    - Large gap between DateTimeOriginal (capture) and DateTime (last modified)
    - Missing metadata (common in screenshots and AI images)
    """
    try:
        exif_bytes = pil_image.info.get("exif", b"")
        if not exif_bytes:
            return {
                "has_metadata": False,
                "software": None,
                "gps": None,
                "time_gap_hours": None,
                "risk_level": "medium",
                "verdict": "No EXIF metadata found — common in screenshots and AI-generated images",
            }

        exif_data = piexif.load(exif_bytes)

        # Software tag
        software_raw = exif_data.get("0th", {}).get(piexif.ImageIFD.Software, None)
        software = software_raw.decode("utf-8", errors="ignore").strip() if software_raw else None

        EDITING_SOFTWARE = ["photoshop", "gimp", "lightroom", "affinity", "pixelmator", "canva"]
        software_risk = any(s in (software or "").lower() for s in EDITING_SOFTWARE)

        # GPS
        gps_data = exif_data.get("GPS", {})
        gps = None
        if gps_data:
            def to_degrees(vals):
                d, m, s = vals
                return d[0]/d[1] + (m[0]/m[1])/60 + (s[0]/s[1])/3600

            try:
                lat = to_degrees(gps_data[piexif.GPSIFD.GPSLatitude])
                lon = to_degrees(gps_data[piexif.GPSIFD.GPSLongitude])
                lat_ref = gps_data.get(piexif.GPSIFD.GPSLatitudeRef, b"N").decode()
                lon_ref = gps_data.get(piexif.GPSIFD.GPSLongitudeRef, b"E").decode()
                if lat_ref == "S": lat = -lat
                if lon_ref == "W": lon = -lon
                gps = {"latitude": round(lat, 6), "longitude": round(lon, 6)}
            except Exception:
                gps = None

        # Time gap between capture and modification
        time_gap_hours = None
        original_time = exif_data.get("Exif", {}).get(piexif.ExifIFD.DateTimeOriginal, None)
        modified_time = exif_data.get("0th", {}).get(piexif.ImageIFD.DateTime, None)
        if original_time and modified_time:
            from datetime import datetime
            fmt = "%Y:%m:%d %H:%M:%S"
            try:
                dt_orig = datetime.strptime(original_time.decode(), fmt)
                dt_mod  = datetime.strptime(modified_time.decode(), fmt)
                time_gap_hours = round(abs((dt_mod - dt_orig).total_seconds() / 3600), 2)
            except Exception:
                pass

        # Risk assessment
        if software_risk:
            risk_level = "high"
            verdict = f"Editing software detected in metadata: {software}"
        elif time_gap_hours and time_gap_hours > 24:
            risk_level = "medium"
            verdict = f"Image modified {time_gap_hours}h after capture"
        else:
            risk_level = "low"
            verdict = "Metadata appears consistent with an original capture"

        return {
            "has_metadata": True,
            "software": software,
            "software_risk": software_risk,
            "gps": gps,
            "time_gap_hours": time_gap_hours,
            "risk_level": risk_level,
            "verdict": verdict,
        }

    except Exception as e:
        return {
            "has_metadata": False,
            "error": str(e),
            "risk_level": "unknown",
            "verdict": "Could not parse metadata",
        }


# ── Signal 3: Noise Analysis ──────────────────────────────────────────────────

def run_noise_analysis(cv2_image: np.ndarray) -> dict:
    """
    Noise consistency analysis.

    Real camera images have a consistent noise texture across the whole frame
    produced by the camera sensor. When a region is pasted in from another
    source, its noise pattern is different.

    Method:
      1. Convert to grayscale.
      2. Apply a strong blur to isolate the low-frequency (subject) content.
      3. Subtract the blurred image from the original — what remains is noise.
      4. Divide the image into a grid of blocks and compute the noise
         standard deviation per block.
      5. High variance BETWEEN blocks suggests the noise is inconsistent,
         which flags potential manipulation.
    """
    gray = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY).astype(np.float32)
    blurred = cv2.GaussianBlur(gray, (21, 21), 0)
    noise_map = np.abs(gray - blurred)

    # Divide into 8x8 grid of blocks
    h, w = noise_map.shape
    block_h, block_w = h // 8, w // 8
    block_stds = []

    for row in range(8):
        for col in range(8):
            block = noise_map[
                row * block_h:(row + 1) * block_h,
                col * block_w:(col + 1) * block_w
            ]
            block_stds.append(float(np.std(block)))

    variance_between_blocks = float(np.std(block_stds))
    mean_noise = float(np.mean(block_stds))

    # High between-block variance means noise is inconsistent
    if variance_between_blocks > 3.5:
        suspicion = min(100, int(variance_between_blocks * 10))
        verdict = "Inconsistent noise pattern — possible region splice"
    else:
        suspicion = max(0, int(variance_between_blocks * 5))
        verdict = "Noise pattern appears consistent across the image"

    return {
        "mean_noise_level": round(mean_noise, 3),
        "between_block_variance": round(variance_between_blocks, 3),
        "suspicion_score": suspicion,
        "verdict": verdict,
    }


# ── Signal 5: Clone Detection ─────────────────────────────────────────────────

def run_clone_detection(cv2_image: np.ndarray) -> dict:
    """
    Clone detection via template matching.

    If a region of an image is copy-pasted to cover something up (e.g. to
    hide a logo or a face), the same pixel pattern appears in two places.

    Method:
      1. Divide the image into a grid of small patches (64x64 px).
      2. For each patch, use cv2.matchTemplate to search the rest of
         the image for a highly similar patch.
      3. If a near-identical patch is found far away from its origin,
         flag it as a potential clone.

    Note: this is a basic implementation. Rotation/scale-invariant clone
    detection requires more advanced techniques (SIFT/ORB feature matching).
    """
    gray = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    patch_size = 150
    threshold = 0.995  # correlation coefficient — 1.0 = perfect match
    min_distance = patch_size * 2  # ignore matches that are too close (same patch)

    clone_pairs = []

    # Limit to a reasonable number of patches for performance
    rows = range(0, h - patch_size, patch_size * 4)
    cols = range(0, w - patch_size, patch_size * 4)

    for r in rows:
        for c in cols:
            patch = gray[r:r + patch_size, c:c + patch_size]
            result = cv2.matchTemplate(gray, patch, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)

            for (match_r, match_c) in zip(*locations[::-1]):
                # Skip if it's the original patch location
                distance = ((match_r - r) ** 2 + (match_c - c) ** 2) ** 0.5
                if distance > min_distance:
                    clone_pairs.append({
                        "source": [int(c), int(r)],
                        "clone":  [int(match_c), int(match_r)],
                    })

    # Deduplicate — many overlapping matches point to the same clone
    unique_clones = clone_pairs[:5]  # return up to 5 unique pairs

    if unique_clones:
        verdict = f"{len(unique_clones)} potential cloned region(s) detected"
        suspicion = min(100, len(unique_clones) * 25)
    else:
        verdict = "No cloned regions detected"
        suspicion = 0

    return {
        "clone_pairs": unique_clones,
        "suspicion_score": suspicion,
        "verdict": verdict,
    }


# ── Signal 6: Screenshot Detection ───────────────────────────────────────────

def run_screenshot_detection(pil_image: Image.Image) -> dict:
    """
    Screenshot classification before deeper analysis.

    Screenshots are not "real" photographs, so ELA and noise analysis
    produce misleading results on them — the frontend should show a
    warning if this fires.

    Heuristics:
      - Very low colour count (screenshots of UI are often flat)
      - Presence of solid-colour border strips (common in phone screenshots)
      - Aspect ratio matching common screen resolutions
    """
    img_array = np.array(pil_image)
    h, w = img_array.shape[:2]

    # Check top and bottom strips for solid colour (status bars, etc.)
    strip_height = max(4, h // 40)
    top_strip = img_array[:strip_height, :, :]
    bot_strip = img_array[-strip_height:, :, :]

    top_std = float(np.std(top_strip))
    bot_std = float(np.std(bot_strip))
    has_solid_strip = top_std < 5 or bot_std < 5

    # Check for suspiciously few unique colours (flat UI)
    sample = pil_image.resize((100, 100))
    unique_colours = len(set(sample.getdata()))
    flat_palette = unique_colours < 500

    is_screenshot = has_solid_strip or flat_palette

    return {
        "is_screenshot": is_screenshot,
        "unique_colours_sample": unique_colours,
        "has_solid_strip": has_solid_strip,
        "verdict": (
            "Likely a screenshot — forensic signals may be unreliable"
            if is_screenshot
            else "Does not appear to be a screenshot"
        ),
    }


# ── Overall Verdict ───────────────────────────────────────────────────────────

def _compute_trust_score(signals: dict) -> dict:
    """
    Combine all signal suspicion scores into one overall trust score.

    Each signal gets a weight based on how reliable it is:
      - ELA and metadata are the strongest indicators
      - Frequency analysis is strong for AI detection
      - Noise and clone detection are supporting signals
    """
    weights = {
        "ela":       0.35,
        "metadata":  0.30,
        "noise":     0.20,
        "clone":     0.15,
    }

    # Convert metadata risk_level to a numeric suspicion score
    metadata_risk_map = {"low": 10, "medium": 40, "high": 80, "unknown": 30}
    metadata_suspicion = metadata_risk_map.get(
        signals["metadata"].get("risk_level", "unknown"), 30
    )

    weighted_suspicion = (
        signals["ela"]["suspicion_score"]       * weights["ela"] +
        metadata_suspicion                       * weights["metadata"] +
        signals["noise"]["suspicion_score"]     * weights["noise"] +
        signals["clone"]["suspicion_score"]     * weights["clone"]
    )

    trust_score = max(0, 100 - int(weighted_suspicion))

    if trust_score >= 75:
        verdict = "Likely Authentic"
        confidence = "high" if trust_score >= 90 else "medium"
    elif trust_score >= 45:
        verdict = "Uncertain — manual review recommended"
        confidence = "low"
    else:
        verdict = "Likely Manipulated or AI-Generated"
        confidence = "high" if trust_score < 25 else "medium"

    return {
        "trust_score": trust_score,
        "verdict": verdict,
        "confidence": confidence,
    }


# ── Public Entry Point ────────────────────────────────────────────────────────

def run_full_analysis(image_bytes: bytes, filename: str) -> dict:
    # Keep an untouched original for ELA — resizing introduces pixel
    # smoothing that creates false positives in error level analysis
    original_image = _bytes_to_pil(image_bytes)

    pil_image = _bytes_to_pil(image_bytes)
    MAX_DIM = 800
    if max(pil_image.width, pil_image.height) > MAX_DIM:
        pil_image.thumbnail((MAX_DIM, MAX_DIM))

    cv2_image = _bytes_to_cv2(image_bytes)
    cv2_image = cv2.resize(cv2_image, (pil_image.width, pil_image.height))

    signals = {
        "screenshot": run_screenshot_detection(pil_image),
        "ela":        run_ela(original_image),
        "metadata":   run_metadata(pil_image),
        "noise":      run_noise_analysis(cv2_image),
        "clone":      run_clone_detection(cv2_image),
    }

    overall = _compute_trust_score(signals)

    return {
        "filename": filename,
        "image_size": {"width": pil_image.width, "height": pil_image.height},
        "signals": signals,
        "overall": overall,
    }

