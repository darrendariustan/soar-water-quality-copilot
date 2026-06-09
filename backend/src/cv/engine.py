import json
import math
from pathlib import Path
from typing import Union

import cv2
import numpy as np

from .models import (
    ImageQuality,
    MatchedColour,
    ParameterReading,
    StripAnalysisResult,
)

_SAFETY_DISCLAIMER = (
    "This is an estimated reading from image analysis and does not replace laboratory testing."
)

_DEFAULT_CHART = Path(__file__).parent / "reference_charts" / "default_strip.json"


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

    lighting_warning = brightness != "acceptable" or blur == "high"

    return ImageQuality(brightness=brightness, blur=blur, lighting_warning=lighting_warning)


def _rgb_to_hsv_tuple(r: int, g: int, b: int) -> list[int]:
    pixel = np.uint8([[[b, g, r]]])
    hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0][0]
    return [int(hsv[0]), int(hsv[1]), int(hsv[2])]


def _delta_e(rgb1: list[int], rgb2: list[int]) -> float:
    """Euclidean distance in RGB space, normalised to [0, 1]."""
    dr = rgb1[0] - rgb2[0]
    dg = rgb1[1] - rgb2[1]
    db = rgb1[2] - rgb2[2]
    dist = math.sqrt(dr * dr + dg * dg + db * db)
    return dist / math.sqrt(3 * 255 * 255)


def match_colour_to_chart(
    sample_rgb: list[int], chart_entries: list[dict]
) -> tuple[dict, float]:
    """Return (best_entry, confidence) where confidence is 1 - normalised_distance."""
    best_entry = None
    best_dist = float("inf")
    for entry in chart_entries:
        d = _delta_e(sample_rgb, entry["rgb"])
        if d < best_dist:
            best_dist = d
            best_entry = entry
    # Scale confidence: distance of 0 -> 1.0, distance >= 0.3 -> 0.0
    confidence = max(0.0, round(1.0 - (best_dist / 0.3), 3))
    return best_entry, confidence


def extract_colour_regions(
    img: np.ndarray, num_regions: int
) -> list[list[int]]:
    """
    Divide the image into num_regions horizontal bands and return mean RGB per band.
    Simple approach suitable for vertical test strips.
    """
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


def analyse_test_strip(
    img: np.ndarray,
    chart_path: Union[str, Path, None] = None,
) -> StripAnalysisResult:
    chart_path = Path(chart_path) if chart_path else _DEFAULT_CHART
    with open(chart_path) as f:
        chart = json.load(f)

    quality = assess_image_quality(img)
    parameters_def = chart["parameters"]
    colour_samples = extract_colour_regions(img, len(parameters_def))

    readings: list[ParameterReading] = []
    for param_def, sample_rgb in zip(parameters_def, colour_samples):
        best_entry, confidence = match_colour_to_chart(sample_rgb, param_def["entries"])
        readings.append(
            ParameterReading(
                name=param_def["name"],
                estimated_value=best_entry["value"],
                unit=param_def["unit"],
                matched_colour=MatchedColour(
                    rgb=best_entry["rgb"],
                    hsv=best_entry["hsv"],
                ),
                confidence=confidence,
            )
        )

    overall_confidence = round(sum(r.confidence for r in readings) / len(readings), 3)

    return StripAnalysisResult(
        parameters=readings,
        overall_confidence=overall_confidence,
        image_quality=quality,
        warnings=[_SAFETY_DISCLAIMER],
    )
