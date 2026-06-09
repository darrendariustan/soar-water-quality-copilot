import numpy as np
import pytest

from backend.src.cv.classifier import classify_water_sample
from backend.src.cv.models import WaterSampleResult


def _solid_image(r: int, g: int, b: int, h: int = 100, w: int = 100) -> np.ndarray:
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :] = [b, g, r]  # BGR
    return img


class TestClassifyWaterSample:
    def test_returns_water_sample_result(self):
        img = _solid_image(200, 210, 220)
        result = classify_water_sample(img)
        assert isinstance(result, WaterSampleResult)
        assert result.image_type == "water_sample"

    def test_includes_safety_warning(self):
        img = _solid_image(200, 210, 220)
        result = classify_water_sample(img)
        assert any("cannot confirm" in w for w in result.warnings)

    def test_confidence_in_valid_range(self):
        img = _solid_image(180, 180, 180)
        result = classify_water_sample(img)
        assert 0.0 <= result.overall_confidence <= 1.0

    def test_very_dark_image_is_opaque(self):
        img = _solid_image(15, 15, 15)
        result = classify_water_sample(img)
        assert result.appearance.clarity == "opaque"

    def test_bright_neutral_image_is_clear(self):
        img = _solid_image(220, 220, 225)
        result = classify_water_sample(img)
        assert result.appearance.clarity == "clear"

    def test_neutral_grey_water_is_colourless(self):
        img = _solid_image(180, 180, 180)
        result = classify_water_sample(img)
        assert result.appearance.colour == "colourless"

    def test_no_particles_on_uniform_image(self):
        # A perfectly uniform image has no contours above threshold
        img = _solid_image(200, 200, 200)
        result = classify_water_sample(img)
        assert result.appearance.visible_particles is False
