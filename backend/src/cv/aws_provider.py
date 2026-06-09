"""
Rekognition-based provider for CV analysis.
Replaces the local OpenCV colour extraction step with Amazon Rekognition
detect_image_properties, while reusing the existing chart-matching logic.
"""
import json
import os
from pathlib import Path
from typing import Union

import boto3
import cv2
import numpy as np

from .engine import (
    _DEFAULT_CHART,
    _PARAM_MESSAGES,
    _WARNINGS,
    _BOILING_RESISTANT_PARAMS,
    _risk_level_to_category,
    load_image,
    match_colour_to_chart,
    _detect_glare,
)
from .models import (
    BoilingRiskFlag,
    ImageQuality,
    MatchedColour,
    ParameterReading,
    StripAnalysisResult,
    WaterAppearance,
    WaterSampleResult,
)

_GLARE_RGB_THRESHOLD = 240

# Labels from Rekognition that suggest turbidity / particles
_CLOUDY_LABELS = {"Fog", "Haze", "Mist", "Smoke", "Pollution"}
_PARTICLE_LABELS = {"Dust", "Powder", "Sand", "Debris", "Dirt"}


def _get_rekognition_client():
    return boto3.client(
        "rekognition",
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    )


def _encode_jpeg(img: np.ndarray) -> bytes:
    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


def _crop_band(img: np.ndarray, idx: int, total: int) -> np.ndarray:
    h = img.shape[0]
    band_h = h // total
    y0 = idx * band_h
    y1 = y0 + band_h if idx < total - 1 else h
    return img[y0:y1, :]


def _rek_quality_to_image_quality(quality_dict: dict, img: np.ndarray) -> ImageQuality:
    brightness_score = quality_dict.get("Brightness", 50)
    sharpness_score = quality_dict.get("Sharpness", 50)

    if brightness_score < 30:
        brightness = "low"
    elif brightness_score > 80:
        brightness = "high"
    else:
        brightness = "acceptable"

    blur = "high" if sharpness_score < 30 else ("medium" if sharpness_score < 60 else "low")
    glare_warning = _detect_glare(img)
    lighting_warning = brightness != "acceptable" or blur == "high" or glare_warning

    return ImageQuality(
        brightness=brightness,
        blur=blur,
        lighting_warning=lighting_warning,
        glare_warning=glare_warning,
    )


def _dominant_rgb_from_response(response: dict) -> list[int]:
    props = response.get("ImagePropertiesResponse", {})
    foreground = props.get("ForegroundColors", [])
    dominant = props.get("DominantColors", [])
    colors = foreground or dominant
    if not colors:
        return [128, 128, 128]
    c = colors[0]
    return [int(c.get("Red", 128)), int(c.get("Green", 128)), int(c.get("Blue", 128))]


def analyse_test_strip_rekognition(
    image_source: Union[np.ndarray, bytes],
    chart_path: Union[str, Path, None] = None,
) -> StripAnalysisResult:
    if isinstance(image_source, (bytes, bytearray)):
        img = load_image(image_source)
    else:
        img = image_source

    chart_path = Path(chart_path) if chart_path else _DEFAULT_CHART
    with open(chart_path) as f:
        chart = json.load(f)

    client = _get_rekognition_client()

    # Assess image quality from full image (one API call)
    full_jpeg = _encode_jpeg(img)
    quality_resp = client.detect_image_properties(
        Image={"Bytes": full_jpeg},
        Features=["IMAGE_QUALITY"],
    )
    raw_quality = quality_resp.get("ImagePropertiesResponse", {}).get("Quality", {})
    image_quality = _rek_quality_to_image_quality(raw_quality, img)

    param_names = list(chart["parameters"].keys())
    readings: list[ParameterReading] = []
    risk_flags: list[BoilingRiskFlag] = []

    for idx, param_name in enumerate(param_names):
        crop = _crop_band(img, idx, len(param_names))
        crop_jpeg = _encode_jpeg(crop)

        rek_resp = client.detect_image_properties(
            Image={"Bytes": crop_jpeg},
            Features=["DOMINANT_COLORS"],
        )
        sample_rgb = _dominant_rgb_from_response(rek_resp)

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
                matched_colour=MatchedColour(rgb=best_entry["rgb"], hsv=best_entry["hsv"]),
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
        image_quality=image_quality,
        warnings=list(_WARNINGS),
    )


def classify_water_sample_rekognition(
    image_source: Union[np.ndarray, bytes],
) -> WaterSampleResult:
    if isinstance(image_source, (bytes, bytearray)):
        img = load_image(image_source)
    else:
        img = image_source

    client = _get_rekognition_client()
    jpeg_bytes = _encode_jpeg(img)

    props_resp = client.detect_image_properties(
        Image={"Bytes": jpeg_bytes},
        Features=["DOMINANT_COLORS", "IMAGE_QUALITY"],
    )
    labels_resp = client.detect_labels(
        Image={"Bytes": jpeg_bytes},
        MinConfidence=60,
    )

    label_names = {label["Name"] for label in labels_resp.get("Labels", [])}
    raw_quality = props_resp.get("ImagePropertiesResponse", {}).get("Quality", {})
    brightness_score = raw_quality.get("Brightness", 50)

    # Clarity: use brightness + turbidity-related label hints
    if label_names & _CLOUDY_LABELS or brightness_score < 40:
        clarity = "cloudy"
    elif brightness_score < 65:
        clarity = "slightly_cloudy"
    elif brightness_score > 80:
        clarity = "clear"
    else:
        clarity = "slightly_cloudy"

    # Colour: use dominant color HSV hue
    dominant_rgb = _dominant_rgb_from_response(props_resp)
    pixel = np.uint8([[[dominant_rgb[2], dominant_rgb[1], dominant_rgb[0]]]])
    hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0][0]
    mean_h, mean_s = int(hsv[0]), int(hsv[1])

    if mean_s < 20:
        colour = "colourless"
    elif 15 <= mean_h <= 35:
        colour = "slightly_yellow"
    elif 8 <= mean_h < 15:
        colour = "slightly_brown"
    elif 35 <= mean_h <= 85:
        colour = "green"
    else:
        colour = "other"

    visible_particles = bool(label_names & _PARTICLE_LABELS)

    overall_confidence = min(raw_quality.get("Sharpness", 50) / 100, 1.0)
    overall_confidence = round(overall_confidence, 3)

    return WaterSampleResult(
        appearance=WaterAppearance(
            clarity=clarity,
            colour=colour,
            visible_particles=visible_particles,
        ),
        overall_confidence=overall_confidence,
        warnings=[
            "Visual appearance alone cannot confirm whether water is safe to drink.",
            "Cloudy water should be settled or filtered before boiling, but boiling does not remove chemical contaminants.",
        ],
    )
