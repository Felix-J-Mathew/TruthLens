"""
services/noise_service.py — Noise Boundary Analysis

HOW NOISE ANALYSIS WORKS:
  Every real camera sensor introduces a small amount of random noise —
  tiny pixel-level variations that are consistent across the whole image
  because they come from the same physical sensor and conditions.

  When a region is copy-pasted, AI-inpainted, or generated separately,
  it has a DIFFERENT noise pattern from the surrounding image. The boundary
  between the edited area and the original has a sudden "step" in noise level.

  We detect this by:
    1. Converting to grayscale and applying a high-pass filter (Laplacian)
       The Laplacian highlights fine texture and noise, suppressing smooth areas.
    2. Dividing the image into a grid of small tiles
    3. Computing the noise level (standard deviation) of each tile
    4. Checking if neighboring tiles have unusually large noise differences

  A real unedited image has fairly uniform noise variance across tiles.
  A manipulated image often shows a sharp jump at the manipulation boundary.

WHAT WE RETURN:
  - noise_map: grid of per-tile noise values (for optional frontend visualization)
  - mean_noise: average noise level across all tiles
  - std_noise: how much noise levels vary between tiles (high = uneven = suspicious)
  - boundary_anomaly: True if std_noise exceeds threshold
  - note: plain-English interpretation
"""

import io
import numpy as np
import cv2


TILE_SIZE = 64          # Each tile is 64x64 pixels
ANOMALY_THRESHOLD = 12  # Standard deviation above which we flag boundary anomaly


def run_noise_analysis(image_bytes: bytes) -> dict:
    """
    Runs noise boundary analysis on raw image bytes.
    """

    # ── Load image via OpenCV ─────────────────────────────────────────────────
    # np.frombuffer converts raw bytes to a numpy array
    # cv2.imdecode turns that into a proper image matrix
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise ValueError("Could not decode image for noise analysis.")

    # ── Apply Laplacian filter ────────────────────────────────────────────────
    # The Laplacian is a "second derivative" filter — it responds strongly to
    # edges and noise, and weakly to smooth gradients.
    # cv2.CV_64F means we want float64 output (avoids clipping negative values)
    laplacian = cv2.Laplacian(img, cv2.CV_64F)

    # ── Tile the image and measure noise per tile ─────────────────────────────
    h, w = laplacian.shape
    noise_map = []

    for y in range(0, h - TILE_SIZE, TILE_SIZE):
        row = []
        for x in range(0, w - TILE_SIZE, TILE_SIZE):
            tile = laplacian[y:y + TILE_SIZE, x:x + TILE_SIZE]
            # Standard deviation of the Laplacian = noise level of this tile
            tile_noise = float(np.std(tile))
            row.append(round(tile_noise, 2))
        if row:
            noise_map.append(row)

    if not noise_map:
        return {"error": "Image too small for tile-based noise analysis."}

    flat = [val for row in noise_map for val in row]
    mean_noise = round(float(np.mean(flat)), 3)
    std_noise = round(float(np.std(flat)), 3)

    boundary_anomaly = std_noise > ANOMALY_THRESHOLD

    if std_noise < 6:
        note = "Noise levels are consistent across the image — no boundary anomalies detected."
    elif std_noise < ANOMALY_THRESHOLD:
        note = "Slight noise variation between regions. Could reflect natural lighting differences."
    else:
        note = (
            f"Significant noise level variation detected across image regions (σ={std_noise}). "
            f"This may indicate that parts of the image have a different origin or were AI-inpainted."
        )

    return {
        "noise_map": noise_map,
        "mean_noise": mean_noise,
        "std_noise": std_noise,
        "threshold_used": ANOMALY_THRESHOLD,
        "boundary_anomaly": boundary_anomaly,
        "note": note,
    }
