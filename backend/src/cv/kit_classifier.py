"""
Kit type classifier.

Local mode: OpenCV heuristics (saturation variance + brightness distribution).
AWS mode: Bedrock Claude Haiku vision for accurate classification.
"""
import json
import os
from typing import Union

import cv2
import numpy as np

_BEDROCK_MODEL = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
_BEDROCK_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

_KNOWN_KIT_TYPES = frozenset({"generic_16_in_1", "heavy_metals_strip", "tds_meter", "unknown"})

_SYSTEM_PROMPT = """You are a water quality test kit identifier. Given an image, determine which type of kit is shown.

Kit types:
- generic_16_in_1: A multi-parameter test strip (paper/plastic strip with several colored pads in a row or column). Usually held or dipped in water. Multiple distinct colored zones visible.
- heavy_metals_strip: A test strip specifically for heavy metals (lead, mercury, copper, cadmium, chromium). Similar appearance to generic strips but typically fewer pads and marketed for heavy metals.
- tds_meter: An electronic digital meter showing a numeric TDS/ppm reading on an LCD or digital display.
- unknown: Cannot determine the kit type from the image.

Return ONLY a valid JSON object — no prose, no markdown fences:
{
  "kit_type": "generic_16_in_1|heavy_metals_strip|tds_meter|unknown",
  "confidence": 0.0-1.0,
  "reasoning": "brief one-sentence explanation"
}"""


def classify_kit_local(img: np.ndarray) -> tuple[str, float]:
    """
    Heuristic kit classification using OpenCV.
    Returns (kit_type, confidence). Confidence is intentionally modest for heuristics.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hue = hsv[:, :, 0].astype(float)
    sat = hsv[:, :, 1]

    # Compute hue std only on saturated pixels to avoid noise from near-grey areas
    saturated = sat > 50
    hue_std = float(np.std(hue[saturated])) if np.sum(saturated) > 100 else 0.0

    _, bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    h, w = img.shape[:2]
    bright_fraction = float(np.sum(bright_mask > 0)) / (h * w)
    mean_brightness = float(np.mean(gray))

    if hue_std > 20:
        # Multiple distinct hues → most likely a multi-pad test strip
        return "generic_16_in_1", 0.55

    if bright_fraction < 0.12 and mean_brightness < 120:
        # Dark image with small bright region → likely TDS meter display
        return "tds_meter", 0.45

    return "unknown", 0.30


def classify_kit_bedrock(image_source: Union[np.ndarray, bytes]) -> tuple[str, float]:
    """Use Bedrock Claude Haiku vision to identify the kit type."""
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
                    {"type": "text", "text": "What type of water quality kit is shown in this image?"},
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
        result = json.loads(text)
        kit_type = result.get("kit_type", "unknown")
        confidence = float(result.get("confidence", 0.5))
        if kit_type not in _KNOWN_KIT_TYPES:
            kit_type = "unknown"
        return kit_type, confidence
    except Exception:
        return "unknown", 0.0
