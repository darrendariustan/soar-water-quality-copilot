import json
import math
from pathlib import Path
from typing import Union

import cv2
import numpy as np

from .models import (
    BoilingRiskFlag,
    ImageQuality,
    MatchedColour,
    ParameterReading,
    StripAnalysisResult,
)

_WARNINGS = [
    "This is an estimated reading from image analysis and does not replace laboratory testing.",
    "Boiling does not remove heavy metals or many chemical contaminants.",
    "This test kit does not test every contaminant.",
    "Final safety guidance must be handled by the Water Quality Agent and Treatment Guidance Agent.",
]

_BOILING_RESISTANT_PARAMS = {"nitrate", "nitrite", "iron"}

_PARAM_MESSAGES = {
    "nitrate": "Boiling does not remove nitrate. Do not treat boiling as sufficient.",
    "nitrite": "Boiling does not remove nitrite. Seek alternative water sources if elevated.",
    "iron": "High iron may indicate corrosion or contamination. Boiling does not remove iron.",
    "pH": "Extreme pH may indicate chemical contamination.",
    "free_chlorine": "High chlorine may indicate over-treatment. Low chlorine may indicate microbial risk.",
    "hardness": "Water hardness is generally not a direct health risk at moderate levels.",
    "turbidity": "Turbid water should be settled or filtered before treatment. Boiling does not remove suspended solids.",
}

_DEFAULT_CHART = Path(__file__).parent / "reference_charts" / "generic_16_in_1.json"

_GLARE_THRESHOLD = 245
_GLARE_MIN_AREA_FRACTION = 0.02


def load_image(source: Union[str, Path, bytes]) -> np.ndarray:
    if isinstance(source, (str, Path)):
        img = cv2.imread(str(source))
        if img is None:
            raise ValueError(f"Could not read image: {source}")
        return img
    arr = np.frombuffer(source, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes")
    return img


def assess_image_quality(img: np.ndarray) -> ImageQuality:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    mean_brightness = float(np.mean(gray))
    if mean_brightness < 60:
        brightness = "low"
    elif mean_brightness > 200:
        brightness = "high"
    else:
        brightness = "acceptable"

    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if laplacian_var < 50:
        blur = "high"
    elif laplacian_var < 200:
        blur = "medium"
    else:
        blur = "low"

    glare_warning = _detect_glare(img)
    lighting_warning = brightness != "acceptable" or blur == "high" or glare_warning

    return ImageQuality(
        brightness=brightness,
        blur=blur,
        lighting_warning=lighting_warning,
        glare_warning=glare_warning,
    )


def _detect_glare(img: np.ndarray) -> bool:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bright_mask = cv2.threshold(gray, _GLARE_THRESHOLD, 255, cv2.THRESH_BINARY)
    total_pixels = img.shape[0] * img.shape[1]
    bright_pixels = int(np.sum(bright_mask > 0))
    return (bright_pixels / total_pixels) > _GLARE_MIN_AREA_FRACTION


def _rgb_to_hsv_tuple(r: int, g: int, b: int) -> list[int]:
    pixel = np.uint8([[[b, g, r]]])
    hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0][0]
    return [int(hsv[0]), int(hsv[1]), int(hsv[2])]


def _delta_e(rgb1: list[int], rgb2: list[int]) -> float:
    dr = rgb1[0] - rgb2[0]
    dg = rgb1[1] - rgb2[1]
    db = rgb1[2] - rgb2[2]
    return math.sqrt(dr * dr + dg * dg + db * db) / math.sqrt(3 * 255 * 255)


def match_colour_to_chart(
    sample_rgb: list[int], chart_entries: list[dict]
) -> tuple[dict, float, float]:
    """Return (best_entry, confidence, raw_distance)."""
    best_entry = None
    best_dist = float("inf")
    for entry in chart_entries:
        d = _delta_e(sample_rgb, entry["rgb"])
        if d < best_dist:
            best_dist = d
            best_entry = entry
    confidence = max(0.0, round(1.0 - (best_dist / 0.3), 3))
    return best_entry, confidence, round(best_dist * 441.67, 2)  # scale to 0–441 Euclidean range


def extract_colour_regions(img: np.ndarray, num_regions: int) -> list[list[int]]:
    h, w = img.shape[:2]
    band_h = h // num_regions
    samples = []
    for i in range(num_regions):
        y0 = i * band_h
        y1 = y0 + band_h if i < num_regions - 1 else h
        band = img[y0:y1, :]
        mean_bgr = cv2.mean(band)[:3]
        rgb = [int(mean_bgr[2]), int(mean_bgr[1]), int(mean_bgr[0])]
        samples.append(rgb)
    return samples


def _risk_level_to_category(risk_level: str, param_name: str) -> str:
    if risk_level == "critical":
        return "treatment_required"
    if risk_level == "warning" and param_name in _BOILING_RESISTANT_PARAMS:
        return "boiling_resistant_warning"
    if risk_level == "warning":
        return "treatment_required"
    return risk_level  # "low" or "neutral"


def analyse_test_strip(
    img: np.ndarray,
    chart_path: Union[str, Path, None] = None,
) -> StripAnalysisResult:
    chart_path = Path(chart_path) if chart_path else _DEFAULT_CHART
    with open(chart_path) as f:
        chart = json.load(f)

    quality = assess_image_quality(img)
    param_names = list(chart["parameters"].keys())
    colour_samples = extract_colour_regions(img, len(param_names))

    readings: list[ParameterReading] = []
    risk_flags: list[BoilingRiskFlag] = []

    for param_name, sample_rgb in zip(param_names, colour_samples):
        entries = chart["parameters"][param_name]
        best_entry, confidence, colour_distance = match_colour_to_chart(sample_rgb, entries)

        risk_level = best_entry.get("risk_level", "low")
        risk_category = _risk_level_to_category(risk_level, param_name)
        message = _PARAM_MESSAGES.get(param_name, "")

        if risk_level in ("warning", "critical"):
            risk_flags.append(
                BoilingRiskFlag(
                    parameter=param_name,
                    risk_level=risk_level,
                    reason=f"Estimated {param_name} result is {best_entry['value']} {best_entry['unit']}. {message}".strip(),
                )
            )

        readings.append(
            ParameterReading(
                name=param_name,
                estimated_value=best_entry["value"],
                unit=best_entry["unit"],
                risk_category=risk_category,
                matched_colour=MatchedColour(
                    rgb=best_entry["rgb"],
                    hsv=best_entry["hsv"],
                ),
                colour_distance=colour_distance,
                confidence=confidence,
                message=message,
            )
        )

    overall_confidence = round(sum(r.confidence for r in readings) / len(readings), 3)

    return StripAnalysisResult(
        kit_id=chart["kit_id"],
        parameters=readings,
        boiling_resistant_risk_flags=risk_flags,
        overall_confidence=overall_confidence,
        image_quality=quality,
        warnings=list(_WARNINGS),
    )
