"""
services/frequency_service.py — Fourier Frequency Analysis

HOW FREQUENCY ANALYSIS WORKS:
  The Fourier Transform decomposes an image into its "frequency components" —
  think of it like breaking sound into its individual musical notes.

  - Low frequencies = broad shapes, smooth gradients (sky, skin)
  - High frequencies = fine details, edges, textures, noise

  Real camera images have a characteristic frequency distribution:
  natural roll-off from low to high frequencies, with realistic noise.

  Fully AI-generated images (from diffusion models like Stable Diffusion,
  Midjourney, DALL-E) show distinctive artifacts in the frequency domain:
    - Unusually clean high-frequency spectrum (too smooth — real cameras add noise)
    - Grid-like periodic patterns from the diffusion process's patch structure
    - Abnormal ratio of low to high frequency energy

  We quantify this by computing the radial average of the frequency spectrum
  and measuring how "steep" the rolloff is. AI images tend to have a
  flatter high-frequency tail than real photographs.

WHAT WE RETURN:
  - spectrum_image_base64: visual of the frequency spectrum (for display)
  - high_freq_ratio: proportion of energy in high frequencies
  - rolloff_slope: how steeply high frequencies drop off
  - ai_generated_likely: True if spectrum matches AI image pattern
  - note: plain-English interpretation
"""

import io
import base64
import numpy as np
import cv2
from PIL import Image


# AI-generated images typically have high_freq_ratio BELOW this value
# (unusually clean / lacking natural camera noise in high frequencies)
AI_HIGH_FREQ_THRESHOLD = 0.08


def run_frequency_analysis(image_bytes: bytes) -> dict:
    """
    Runs Fourier frequency analysis on raw image bytes.
    """

    # ── Load and prepare image ────────────────────────────────────────────────
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise ValueError("Could not decode image for frequency analysis.")

    # Resize to standard size for consistent analysis
    img = cv2.resize(img, (512, 512))

    # ── Apply 2D Fourier Transform ────────────────────────────────────────────
    # np.fft.fft2 computes the 2D discrete Fourier transform.
    # fftshift moves the zero-frequency component to the center of the spectrum,
    # which makes the output visually interpretable (DC component in middle).
    f_transform = np.fft.fft2(img.astype(np.float32))
    f_shifted = np.fft.fftshift(f_transform)

    # Magnitude spectrum (log scale for visibility)
    magnitude = np.abs(f_shifted)
    log_magnitude = np.log1p(magnitude)  # log1p = log(1 + x), avoids log(0)

    # ── Compute radial frequency profile ─────────────────────────────────────
    # For each pixel in the spectrum, compute its distance from the center.
    # Then average magnitudes at each radius to get the radial profile.
    h, w = log_magnitude.shape
    cy, cx = h // 2, w // 2

    Y, X = np.ogrid[:h, :w]
    radius_map = np.sqrt((X - cx)**2 + (Y - cy)**2).astype(int)

    max_radius = min(cx, cy)
    radial_profile = np.zeros(max_radius)
    counts = np.zeros(max_radius)

    for r in range(max_radius):
        mask = radius_map == r
        if mask.any():
            radial_profile[r] = log_magnitude[mask].mean()
            counts[r] = mask.sum()

    # ── Compute high-frequency energy ratio ───────────────────────────────────
    # Low frequencies: inner 20% of radius
    # High frequencies: outer 40% of radius
    low_cutoff = int(max_radius * 0.2)
    high_cutoff = int(max_radius * 0.6)

    low_energy = float(np.mean(radial_profile[:low_cutoff]))
    high_energy = float(np.mean(radial_profile[high_cutoff:]))

    total_energy = low_energy + high_energy + 1e-9  # avoid div by zero
    high_freq_ratio = round(high_energy / total_energy, 4)

    # ── Compute rolloff slope ─────────────────────────────────────────────────
    # How steeply does energy drop from low to high freq?
    # A very flat slope = too clean = AI-generated
    if low_energy > 0:
        rolloff_slope = round((low_energy - high_energy) / low_energy, 4)
    else:
        rolloff_slope = 0.0

    ai_generated_likely = high_freq_ratio < AI_HIGH_FREQ_THRESHOLD

    # ── Visualize spectrum as base64 image ────────────────────────────────────
    spectrum_normalized = cv2.normalize(
        log_magnitude, None, 0, 255, cv2.NORM_MINMAX
    ).astype(np.uint8)
    spectrum_colored = cv2.applyColorMap(spectrum_normalized, cv2.COLORMAP_INFERNO)
    _, buffer = cv2.imencode(".jpg", spectrum_colored)
    spectrum_b64 = base64.b64encode(buffer).decode("utf-8")

    # ── Interpret result ──────────────────────────────────────────────────────
    if not ai_generated_likely:
        note = "Frequency spectrum shows normal high-frequency content consistent with a real camera image."
    else:
        note = (
            f"Frequency spectrum shows unusually low high-frequency energy (ratio={high_freq_ratio}). "
            f"AI-generated images lack natural camera sensor noise in high frequencies — "
            f"this pattern may indicate a fully synthetic image."
        )

    return {
        "spectrum_image_base64": spectrum_b64,
        "high_freq_ratio": high_freq_ratio,
        "rolloff_slope": rolloff_slope,
        "threshold_used": AI_HIGH_FREQ_THRESHOLD,
        "ai_generated_likely": ai_generated_likely,
        "note": note,
    }
