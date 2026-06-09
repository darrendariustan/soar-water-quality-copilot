"""
AWS Bedrock vision provider for CV analysis.
Uses Claude Haiku (vision) via Bedrock to analyse test strip images and water samples.
Returns the same Pydantic models as the local OpenCV provider — drop-in replacement.
"""
import base64
import json
import os
from pathlib import Path
from typing import Union

import boto3
import cv2
import numpy as np

from .engine import _DEFAULT_CHART, _WARNINGS, load_image
from .models import (
    BoilingRiskFlag,
    ImageQuality,
    MatchedColour,
    ParameterReading,
    StripAnalysisResult,
    WaterAppearance,
    WaterSampleResult,
)

_BEDROCK_MODEL = os.getenv(
    "BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0"
)
_BEDROCK_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")  # cross-region inference profile requires us-east-1

_STRIP_SYSTEM_PROMPT = """You are a water quality test strip analyser. You will be given:
1. An image of a water test strip
2. A JSON reference chart with expected parameter names and colour entries

Analyse the image carefully. For each parameter in the chart, identify the colour in the
corresponding zone of the strip and match it to the closest chart entry.

Return ONLY a valid JSON object — no prose, no markdown fences. Schema:
{
  "parameters": [
    {
      "name": "string",
      "estimated_value": "string",
      "unit": "string",
      "risk_level": "low|neutral|warning|critical",
      "matched_rgb": [R, G, B],
      "matched_hsv": [H, S, V],
      "confidence": 0.0-1.0,
      "colour_distance": 0.0-441.0
    }
  ],
  "image_quality": {
    "brightness": "low|acceptable|high",
    "blur": "low|medium|high",
    "lighting_warning": true|false,
    "glare_warning": true|false
  },
  "notes": "optional short observation"
}

Rules:
- Never say the water is safe or unsafe to drink.
- Base confidence on how closely the strip colour matches the chart entry.
- If the image is blurry or poorly lit, set lighting_warning or glare_warning accordingly.
- colour_distance is a 0-441 scale (0 = perfect match, 441 = maximum possible distance)."""

_SAMPLE_SYSTEM_PROMPT = """You are a water clarity analyser. Examine the water sample image.

Return ONLY a valid JSON object — no prose, no markdown fences. Schema:
{
  "clarity": "clear|slightly_cloudy|cloudy|opaque",
  "colour": "colourless|slightly_yellow|slightly_brown|green|other",
  "visible_particles": true|false,
  "overall_confidence": 0.0-1.0
}

Rules:
- Never say the water is safe or unsafe to drink.
- Base confidence on image quality and how clear the water appearance is."""

_BOILING_RESISTANT = {"nitrate", "nitrite", "iron"}
_PARAM_MESSAGES = {
    "nitrate": "Boiling does not remove nitrate. Do not treat boiling as sufficient.",
    "nitrite": "Boiling does not remove nitrite. Seek alternative water sources if elevated.",
    "iron": "High iron may indicate corrosion or contamination. Boiling does not remove iron.",
    "pH": "Extreme pH may indicate chemical contamination.",
    "free_chlorine": "High chlorine may indicate over-treatment. Low chlorine may indicate microbial risk.",
    "hardness": "Water hardness is generally not a direct health risk at moderate levels.",
    "turbidity": "Turbid water should be settled or filtered before treatment.",
}


def _bedrock_client():
    return boto3.client("bedrock-runtime", region_name=_BEDROCK_REGION)


def _encode_image_b64(img: np.ndarray) -> str:
    _, buf = cv2.imencode(".jpg", img)
    return base64.standard_b64encode(buf.tobytes()).decode("utf-8")


def _invoke(client, system: str, user_text: str, image_b64: str) -> dict:
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "system": system,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                    {"type": "text", "text": user_text},
                ],
            }
        ],
    }
    resp = client.invoke_model(modelId=_BEDROCK_MODEL, body=json.dumps(body))
    text = json.loads(resp["body"].read())["content"][0]["text"]
    return json.loads(text)


def _risk_category(risk_level: str, param_name: str) -> str:
    if risk_level == "critical":
        return "treatment_required"
    if risk_level == "warning" and param_name in _BOILING_RESISTANT:
        return "boiling_resistant_warning"
    if risk_level == "warning":
        return "treatment_required"
    return risk_level


def analyse_test_strip_bedrock(
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

    # Build a compact chart summary for the prompt
    param_summary = {
        name: [{"value": e["value"], "unit": e["unit"], "risk_level": e["risk_level"]} for e in entries]
        for name, entries in chart["parameters"].items()
    }
    user_text = (
        f"Reference chart (kit: {chart['kit_id']}):\n{json.dumps(param_summary, indent=2)}\n\n"
        "Analyse the test strip in the image against this chart."
    )

    image_b64 = _encode_image_b64(img)
    client = _bedrock_client()

    try:
        result = _invoke(client, _STRIP_SYSTEM_PROMPT, user_text, image_b64)
    except Exception as exc:
        # Graceful fallback: return low-confidence result with error warning
        return StripAnalysisResult(
            kit_id=chart["kit_id"],
            parameters=[],
            boiling_resistant_risk_flags=[],
            overall_confidence=0.0,
            image_quality=ImageQuality(brightness="acceptable", blur="low", lighting_warning=False, glare_warning=False),
            warnings=list(_WARNINGS) + [f"Bedrock analysis unavailable: {exc}"],
        )

    readings: list[ParameterReading] = []
    risk_flags: list[BoilingRiskFlag] = []

    for p in result.get("parameters", []):
        name = p["name"]
        risk_level = p.get("risk_level", "low")
        cat = _risk_category(risk_level, name)
        message = _PARAM_MESSAGES.get(name, "")

        if risk_level in ("warning", "critical"):
            risk_flags.append(BoilingRiskFlag(
                parameter=name,
                risk_level=risk_level,
                reason=f"Estimated {name} is {p['estimated_value']} {p.get('unit','')}. {message}".strip(),
            ))

        readings.append(ParameterReading(
            name=name,
            estimated_value=p["estimated_value"],
            unit=p.get("unit", ""),
            risk_category=cat,
            matched_colour=MatchedColour(
                rgb=p.get("matched_rgb", [128, 128, 128]),
                hsv=p.get("matched_hsv", [0, 0, 128]),
            ),
            colour_distance=float(p.get("colour_distance", 0.0)),
            confidence=float(p.get("confidence", 0.5)),
            message=message,
        ))

    iq = result.get("image_quality", {})
    overall = round(sum(r.confidence for r in readings) / max(len(readings), 1), 3)

    return StripAnalysisResult(
        kit_id=chart["kit_id"],
        parameters=readings,
        boiling_resistant_risk_flags=risk_flags,
        overall_confidence=overall,
        image_quality=ImageQuality(
            brightness=iq.get("brightness", "acceptable"),
            blur=iq.get("blur", "low"),
            lighting_warning=bool(iq.get("lighting_warning", False)),
            glare_warning=bool(iq.get("glare_warning", False)),
        ),
        warnings=list(_WARNINGS),
    )


def classify_water_sample_bedrock(
    image_source: Union[np.ndarray, bytes],
) -> WaterSampleResult:
    if isinstance(image_source, (bytes, bytearray)):
        img = load_image(image_source)
    else:
        img = image_source

    image_b64 = _encode_image_b64(img)
    client = _bedrock_client()

    try:
        result = _invoke(client, _SAMPLE_SYSTEM_PROMPT, "Analyse the water sample in this image.", image_b64)
    except Exception as exc:
        return WaterSampleResult(
            appearance=WaterAppearance(clarity="clear", colour="colourless", visible_particles=False),
            overall_confidence=0.0,
            warnings=[
                "Visual appearance alone cannot confirm whether water is safe to drink.",
                f"Bedrock analysis unavailable: {exc}",
            ],
        )

    return WaterSampleResult(
        appearance=WaterAppearance(
            clarity=result.get("clarity", "clear"),
            colour=result.get("colour", "colourless"),
            visible_particles=bool(result.get("visible_particles", False)),
        ),
        overall_confidence=float(result.get("overall_confidence", 0.5)),
        warnings=[
            "Visual appearance alone cannot confirm whether water is safe to drink.",
            "Cloudy water should be settled or filtered before boiling, but boiling does not remove chemical contaminants.",
        ],
    )


# Expose under the same names the server imports
analyse_test_strip_rekognition = analyse_test_strip_bedrock
classify_water_sample_rekognition = classify_water_sample_bedrock
