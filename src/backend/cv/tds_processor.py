"""
TDS meter image processor.

Local mode: returns manual_review_required (7-segment OCR needs a vision model).
AWS mode: uses Bedrock Claude Haiku vision to read the digital display.
"""
import json
import os
from pathlib import Path
from typing import Union

import cv2
import numpy as np

from .models import TDSResult

_THRESHOLDS_PATH = Path(__file__).parent / "reference_charts" / "tds_thresholds.json"

_BEDROCK_MODEL = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
_BEDROCK_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

_SYSTEM_PROMPT = """You are a TDS (Total Dissolved Solids) meter reader. You will be given an image of a TDS meter.

Read the numeric value shown on the digital/LCD display.

Return ONLY a valid JSON object — no prose, no markdown fences:
{
  "detected_text": "string (raw text from display, e.g. '342')",
  "parsed_value": number or null,
  "unit": "string (e.g. 'ppm' or 'mg/L', default 'ppm' if not visible)",
  "confidence": 0.0-1.0
}

Rules:
- If the display is off, unreadable, or this is not a TDS meter, set parsed_value to null and confidence to 0.
- Do not say whether water is safe or unsafe to drink.
- ppm and mg/L are equivalent for TDS (1 ppm = 1 mg/L)."""


def _load_thresholds() -> list[dict]:
    if _THRESHOLDS_PATH.exists():
        with open(_THRESHOLDS_PATH) as f:
            return json.load(f)["thresholds"]
    return [
        {"min": 0,    "max": 300,  "risk_category": "low",     "message": "TDS within acceptable range."},
        {"min": 301,  "max": 500,  "risk_category": "caution", "message": "Elevated TDS. Monitor."},
        {"min": 501,  "max": 900,  "risk_category": "warning", "message": "High TDS. Treatment recommended."},
        {"min": 901,  "max": 1200, "risk_category": "warning", "message": "Very high TDS. Not suitable without treatment."},
        {"min": 1201, "max": None, "risk_category": "high",    "message": "Extremely high TDS. Unsuitable for drinking."},
    ]


def _categorise(value: float) -> tuple[str, str]:
    for t in _load_thresholds():
        lo = t["min"]
        hi = t.get("max") if t.get("max") is not None else float("inf")
        if lo <= value <= hi:
            return t["risk_category"], t["message"]
    return "unknown", "Could not categorise TDS value."


def process_tds_local(image_source: Union[np.ndarray, bytes]) -> TDSResult:
    """Local fallback — cannot OCR digital displays without a vision model."""
    return TDSResult(
        detected_text="",
        parsed_value=None,
        unit="ppm",
        confidence=0.0,
        risk_category="unknown",
        status="manual_review_required",
        message="TDS meter OCR requires vision AI. Set CV_PROVIDER=aws to enable automatic reading.",
    )


def process_tds_bedrock(image_source: Union[np.ndarray, bytes]) -> TDSResult:
    """Use Bedrock Claude Haiku vision to OCR the TDS meter display."""
    import base64

    import boto3

    from .engine import load_image

    if isinstance(image_source, (bytes, bytearray)):
        img = load_image(image_source)
    else:
        img = image_source

    _, buf = cv2.imencode(".jpg", img)
    image_b64 = base64.standard_b64encode(buf.tobytes()).decode("utf-8")

    client = boto3.client("bedrock-runtime", region_name=_BEDROCK_REGION)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 256,
        "system": _SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64},
                    },
                    {"type": "text", "text": "Read the TDS value from this meter display."},
                ],
            }
        ],
    }

    try:
        resp = client.invoke_model(modelId=_BEDROCK_MODEL, body=json.dumps(body))
        payload = json.loads(resp["body"].read())
        text = payload["content"][0]["text"].strip()
        if text.startswith("```"):
            newline = text.find("\n")
            text = text[newline + 1:] if newline != -1 else text[3:]
            if text.rstrip().endswith("```"):
                text = text[: text.rstrip().rfind("```")].strip()
        raw = json.loads(text)
    except Exception as exc:
        return TDSResult(
            detected_text="",
            parsed_value=None,
            unit="ppm",
            confidence=0.0,
            risk_category="unknown",
            status="manual_review_required",
            message=f"Bedrock TDS OCR unavailable: {exc}",
        )

    detected = raw.get("detected_text", "")
    parsed = raw.get("parsed_value")
    unit = raw.get("unit", "ppm")
    confidence = float(raw.get("confidence", 0.5))

    if parsed is not None:
        risk_category, message = _categorise(float(parsed))
        status = "processed"
    else:
        risk_category = "unknown"
        message = "Could not read TDS value from display."
        status = "manual_review_required"

    return TDSResult(
        detected_text=detected,
        parsed_value=parsed,
        unit=unit,
        confidence=confidence,
        risk_category=risk_category,
        status=status,
        message=message,
    )
