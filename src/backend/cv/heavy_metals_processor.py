"""
Heavy metals strip processor.
Delegates to engine.analyse_test_strip() with the heavy_metals_strip chart.
All heavy metal parameters are boiling-resistant.
"""
from pathlib import Path
from typing import Union

import numpy as np

from .engine import analyse_test_strip, load_image
from .models import StripAnalysisResult

_HEAVY_METALS_CHART = Path(__file__).parent / "reference_charts" / "heavy_metals_strip.json"

_METAL_MESSAGES = {
    "lead":     "Lead is toxic at any level. Boiling does not remove lead. Seek laboratory confirmation immediately.",
    "mercury":  "Mercury is highly toxic. Boiling does not remove mercury. Seek laboratory confirmation immediately.",
    "copper":   "Elevated copper may indicate pipe corrosion. Boiling does not remove copper.",
    "cadmium":  "Cadmium accumulates in the body. Boiling does not remove cadmium. Seek laboratory confirmation.",
    "chromium": "Chromium (Cr-VI) is a known carcinogen. Boiling does not remove chromium. Seek laboratory confirmation.",
}


def analyse_heavy_metals_strip(
    image_source: Union[np.ndarray, bytes],
) -> StripAnalysisResult:
    if isinstance(image_source, (bytes, bytearray)):
        img = load_image(image_source)
    else:
        img = image_source

    result = analyse_test_strip(img, chart_path=_HEAVY_METALS_CHART)

    enriched_params = [
        p.model_copy(update={"message": _METAL_MESSAGES.get(p.name, p.message)})
        for p in result.parameters
    ]
    enriched_flags = [
        f.model_copy(update={"reason": _METAL_MESSAGES.get(f.parameter, f.reason)})
        for f in result.boiling_resistant_risk_flags
    ]

    return result.model_copy(update={
        "parameters": enriched_params,
        "boiling_resistant_risk_flags": enriched_flags,
    })
