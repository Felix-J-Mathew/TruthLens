"""
services/metadata_service.py — EXIF Metadata Analysis

HOW METADATA ANALYSIS WORKS:
  Every digital photo carries hidden data called EXIF metadata —
  the camera model, GPS coordinates, software used to edit it,
  date/time taken, and more.

  Manipulated images often reveal themselves through metadata:
    - Software field says "Adobe Photoshop" or an AI tool name
    - Large gap between DateTimeOriginal (taken) and DateTime (last modified)
    - GPS coordinates that contradict the claimed location
    - Metadata stripped entirely (common after re-export from editing tools)

WHAT WE RETURN:
  - raw_fields: all readable EXIF tags (shown in metadata table on frontend)
  - software: what program last touched the file
  - software_risk: LOW / MEDIUM / HIGH based on software classification
  - capture_time / modify_time: when photo was taken vs last saved
  - time_gap_hours: difference between the two
  - gps: { latitude, longitude } if GPS data present
  - risk_level: overall risk classification
  - flags: list of specific concerns found
"""

import io
import math
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif


# Software keywords that suggest editing or AI generation
HIGH_RISK_SOFTWARE = [
    "photoshop", "gimp", "lightroom", "affinity", "pixelmator",
    "stable diffusion", "midjourney", "dall-e", "firefly",
    "canva", "snapseed", "facetune",
]

MEDIUM_RISK_SOFTWARE = [
    "preview", "paint", "photos", "windows photo",
]


def run_metadata(image_bytes: bytes, filename: str) -> dict:
    """
    Extracts and interprets EXIF metadata from image bytes.
    """

    image = Image.open(io.BytesIO(image_bytes))
    raw_exif = image._getexif()  # Returns dict of {tag_id: value} or None

    flags = []
    raw_fields = {}
    software = None
    capture_time = None
    modify_time = None
    gps = None

    # ── No EXIF at all ────────────────────────────────────────────────────────
    if raw_exif is None:
        flags.append("No EXIF metadata found — may have been stripped after editing.")
        return {
            "raw_fields": {},
            "software": None,
            "software_risk": "MEDIUM",
            "capture_time": None,
            "modify_time": None,
            "time_gap_hours": None,
            "gps": None,
            "risk_level": "MEDIUM",
            "flags": flags,
        }

    # ── Parse all EXIF fields ─────────────────────────────────────────────────
    for tag_id, value in raw_exif.items():
        tag_name = TAGS.get(tag_id, str(tag_id))

        # Skip binary blobs (MakerNote etc.) — not useful to display
        if isinstance(value, bytes):
            continue

        raw_fields[tag_name] = str(value)

        if tag_name == "Software":
            software = str(value)
        elif tag_name == "DateTimeOriginal":
            capture_time = str(value)
        elif tag_name == "DateTime":
            modify_time = str(value)
        elif tag_name == "GPSInfo":
            gps = parse_gps(value)

    # ── Software risk classification ──────────────────────────────────────────
    software_risk = "LOW"
    if software:
        sw_lower = software.lower()
        if any(k in sw_lower for k in HIGH_RISK_SOFTWARE):
            software_risk = "HIGH"
            flags.append(f"Software field indicates editing tool: '{software}'")
        elif any(k in sw_lower for k in MEDIUM_RISK_SOFTWARE):
            software_risk = "MEDIUM"
            flags.append(f"Software field: '{software}' — minor processing likely.")
    else:
        flags.append("No software field in metadata.")

    # ── Time gap analysis ─────────────────────────────────────────────────────
    time_gap_hours = None
    if capture_time and modify_time and capture_time != modify_time:
        try:
            from datetime import datetime
            fmt = "%Y:%m:%d %H:%M:%S"
            t1 = datetime.strptime(capture_time, fmt)
            t2 = datetime.strptime(modify_time, fmt)
            time_gap_hours = round(abs((t2 - t1).total_seconds()) / 3600, 2)
            if time_gap_hours > 1:
                flags.append(
                    f"Capture-to-modification gap: {time_gap_hours} hours — "
                    f"image was opened and re-saved after being taken."
                )
        except Exception:
            pass

    # ── Overall risk level ────────────────────────────────────────────────────
    if software_risk == "HIGH" or (time_gap_hours and time_gap_hours > 24):
        risk_level = "HIGH"
    elif software_risk == "MEDIUM" or (time_gap_hours and time_gap_hours > 1):
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "raw_fields": raw_fields,
        "software": software,
        "software_risk": software_risk,
        "capture_time": capture_time,
        "modify_time": modify_time,
        "time_gap_hours": time_gap_hours,
        "gps": gps,
        "risk_level": risk_level,
        "flags": flags,
    }


def parse_gps(gps_info: dict) -> dict | None:
    """
    Converts raw GPS EXIF data (degrees/minutes/seconds tuples) into
    decimal latitude/longitude that can be placed on a map.
    """
    try:
        gps_data = {}
        for key, val in gps_info.items():
            tag = GPSTAGS.get(key, key)
            gps_data[tag] = val

        def dms_to_decimal(dms, ref):
            # dms = ((deg_num, deg_den), (min_num, min_den), (sec_num, sec_den))
            degrees = dms[0][0] / dms[0][1]
            minutes = dms[1][0] / dms[1][1] / 60
            seconds = dms[2][0] / dms[2][1] / 3600
            decimal = degrees + minutes + seconds
            if ref in ["S", "W"]:
                decimal = -decimal
            return round(decimal, 6)

        lat = dms_to_decimal(gps_data["GPSLatitude"], gps_data["GPSLatitudeRef"])
        lon = dms_to_decimal(gps_data["GPSLongitude"], gps_data["GPSLongitudeRef"])
        return {"latitude": lat, "longitude": lon}
    except Exception:
        return None
