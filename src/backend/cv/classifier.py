import cv2
import numpy as np

from .models import WaterAppearance, WaterSampleResult

_WARNINGS = [
    "Visual appearance alone cannot confirm whether water is safe to drink.",
    "Cloudy water should be settled or filtered before boiling, but boiling does not remove chemical contaminants.",
]

_PARTICLE_MIN_AREA = 30
_PARTICLE_THRESHOLD = 5


def _assess_clarity(gray: np.ndarray) -> str:
    mean_val = float(np.mean(gray))
    # Brightness is the primary proxy for turbidity: brighter = clearer
    if mean_val > 190:
        return "clear"
    elif mean_val > 140:
        return "slightly_cloudy"
    elif mean_val > 80:
        return "cloudy"
    return "opaque"


def _assess_colour(img_bgr: np.ndarray) -> str:
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mean_h = float(np.mean(hsv[:, :, 0]))
    mean_s = float(np.mean(hsv[:, :, 1]))

    if mean_s < 20:
        return "colourless"
    if 15 <= mean_h <= 35:
        return "slightly_yellow"
    if 8 <= mean_h < 15:
        return "slightly_brown"
    if 35 <= mean_h <= 85:
        return "green"
    return "other"


def _detect_particles(gray: np.ndarray) -> bool:
    # Brighten then threshold to find dark specks
    brightened = cv2.convertScaleAbs(gray, alpha=1.4, beta=30)
    _, thresh = cv2.threshold(brightened, 80, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    significant = [c for c in contours if cv2.contourArea(c) >= _PARTICLE_MIN_AREA]
    return len(significant) >= _PARTICLE_THRESHOLD


def _estimate_confidence(gray: np.ndarray) -> float:
    mean_brightness = float(np.mean(gray))
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    brightness_score = 1.0 - abs(mean_brightness - 128) / 128
    blur_score = min(laplacian_var / 300, 1.0)
    return round((brightness_score + blur_score) / 2, 3)


def classify_water_sample(img: np.ndarray) -> WaterSampleResult:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    clarity = _assess_clarity(gray)
    colour = _assess_colour(img)
    visible_particles = _detect_particles(gray)
    overall_confidence = _estimate_confidence(gray)

    return WaterSampleResult(
        appearance=WaterAppearance(
            clarity=clarity,
            colour=colour,
            visible_particles=visible_particles,
        ),
        overall_confidence=overall_confidence,
        warnings=list(_WARNINGS),
    )
