"""
services/clone_service.py — Clone / Copy-Paste Detection

HOW CLONE DETECTION WORKS:
  A common manipulation technique is "copy-paste cloning" — duplicating a
  region of the image to cover something up or repeat a background element.

  We detect this by:
    1. Dividing the image into overlapping patches (small windows)
    2. For each patch, using template matching to search the rest of the
       image for a visually identical patch
    3. If a strong match is found at a different location (not just the patch
       itself), we flag it as a cloned region

  Template matching slides the patch across the image and computes a
  similarity score at each position. A score near 1.0 = near-perfect copy.

  We run this on a DOWNSCALED image to keep it fast on low-resource hardware.

LIMITATIONS:
  This is basic template matching — it won't catch clones that have been
  rotated, flipped, or color-adjusted. For a college project this level is fine.
  More advanced methods exist (PatchMatch, keypoint-based) but require
  significantly more compute.

WHAT WE RETURN:
  - clones_found: True if any strong copy-paste regions detected
  - clone_regions: list of { source_x, source_y, match_x, match_y, score }
  - note: plain-English interpretation
"""

import io
import numpy as np
import cv2


PATCH_SIZE = 32         # Size of each patch window in pixels
STRIDE = 24             # How far to move between patches (overlap = PATCH_SIZE - STRIDE)
CLONE_THRESHOLD = 0.98  # Similarity score above which we call it a clone
MIN_DISTANCE = 40       # Minimum pixel distance — ignore matches too close to source
MAX_PATCHES = 80        # Cap on patches to check (performance on low-RAM hardware)
TARGET_SIZE = 256       # Downscale image to this before analysis


def run_clone_detection(image_bytes: bytes) -> dict:
    """
    Runs basic copy-paste clone detection on raw image bytes.
    """

    # ── Load and downscale ────────────────────────────────────────────────────
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise ValueError("Could not decode image for clone detection.")

    img = cv2.resize(img, (TARGET_SIZE, TARGET_SIZE))
    h, w = img.shape

    clone_regions = []
    patches_checked = 0

    # ── Iterate over patches ──────────────────────────────────────────────────
    for y in range(0, h - PATCH_SIZE, STRIDE):
        for x in range(0, w - PATCH_SIZE, STRIDE):
            if patches_checked >= MAX_PATCHES:
                break

            patch = img[y:y + PATCH_SIZE, x:x + PATCH_SIZE].astype(np.float32)

            # Template matching: slide the patch across the whole image
            # TM_CCOEFF_NORMED returns values in [-1, 1]; 1.0 = perfect match
            result = cv2.matchTemplate(img.astype(np.float32), patch, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            match_x, match_y = max_loc

            # Ignore: match too close to source (it's just finding itself)
            distance = np.sqrt((match_x - x)**2 + (match_y - y)**2)
            if distance < MIN_DISTANCE:
                patches_checked += 1
                continue

            if max_val >= CLONE_THRESHOLD:
                clone_regions.append({
                    "source_x": int(x),
                    "source_y": int(y),
                    "match_x": int(match_x),
                    "match_y": int(match_y),
                    "score": round(float(max_val), 4),
                })

            patches_checked += 1
        else:
            continue
        break  # Break outer loop too if MAX_PATCHES hit

    # Deduplicate: remove near-duplicate clone reports
    clone_regions = deduplicate_clones(clone_regions)
    clones_found = len(clone_regions) > 0

    if not clones_found:
        note = "No copy-paste cloning patterns detected."
    else:
        note = (
            f"{len(clone_regions)} potential cloned region(s) found. "
            f"Regions with high similarity at distinct locations suggest "
            f"content may have been duplicated within this image."
        )

    return {
        "clones_found": clones_found,
        "clone_count": len(clone_regions),
        "clone_regions": clone_regions[:10],  # Cap output size
        "note": note,
    }


def deduplicate_clones(regions: list, proximity: int = 20) -> list:
    """Remove clone detections that are spatially too close to each other."""
    if not regions:
        return regions

    deduplicated = [regions[0]]
    for region in regions[1:]:
        too_close = False
        for kept in deduplicated:
            dist = np.sqrt(
                (region["source_x"] - kept["source_x"])**2 +
                (region["source_y"] - kept["source_y"])**2
            )
            if dist < proximity:
                too_close = True
                break
        if not too_close:
            deduplicated.append(region)

    return deduplicated
