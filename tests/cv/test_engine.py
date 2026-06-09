import numpy as np
import pytest

from backend.src.cv.engine import (
    assess_image_quality,
    extract_colour_regions,
    match_colour_to_chart,
    analyse_test_strip,
)
from backend.src.cv.models import StripAnalysisResult


def _solid_image(r: int, g: int, b: int, h: int = 100, w: int = 50) -> np.ndarray:
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :] = [b, g, r]  # BGR
    return img


class TestAssessImageQuality:
    def test_bright_and_sharp_image(self):
        img = _solid_image(200, 200, 200)
        quality = assess_image_quality(img)
        assert quality.brightness == "acceptable"

    def test_very_dark_image_flags_low_brightness(self):
        img = _solid_image(20, 20, 20)
        quality = assess_image_quality(img)
        assert quality.brightness == "low"

    def test_very_bright_image_flags_high_brightness(self):
        img = _solid_image(250, 250, 250)
        quality = assess_image_quality(img)
        assert quality.brightness == "high"

    def test_uniform_image_has_high_blur(self):
        img = _solid_image(128, 128, 128)
        quality = assess_image_quality(img)
        assert quality.blur == "high"

    def test_glare_warning_on_very_bright_image(self):
        img = _solid_image(248, 248, 248)
        quality = assess_image_quality(img)
        assert quality.glare_warning is True

    def test_no_glare_on_mid_brightness(self):
        img = _solid_image(150, 150, 150)
        quality = assess_image_quality(img)
        assert quality.glare_warning is False

    def test_returns_glare_warning_field(self):
        img = _solid_image(128, 128, 128)
        quality = assess_image_quality(img)
        assert hasattr(quality, "glare_warning")


class TestExtractColourRegions:
    def test_returns_correct_number_of_regions(self):
        img = _solid_image(100, 150, 200, h=100)
        regions = extract_colour_regions(img, 5)
        assert len(regions) == 5

    def test_each_region_has_three_channels(self):
        img = _solid_image(100, 150, 200, h=100)
        for region in extract_colour_regions(img, 3):
            assert len(region) == 3

    def test_solid_image_same_colour_in_all_regions(self):
        img = _solid_image(120, 80, 40, h=100)
        regions = extract_colour_regions(img, 4)
        for rgb in regions:
            assert abs(rgb[0] - 120) <= 2
            assert abs(rgb[1] - 80) <= 2
            assert abs(rgb[2] - 40) <= 2


class TestMatchColourToChart:
    def test_exact_match_gives_high_confidence(self):
        entries = [
            {"value": "7.0", "unit": "", "rgb": [255, 180, 80], "hsv": [30, 175, 255], "risk_level": "neutral"},
            {"value": "8.0", "unit": "", "rgb": [120, 200, 80], "hsv": [96, 150, 200], "risk_level": "neutral"},
        ]
        best, confidence, dist = match_colour_to_chart([255, 180, 80], entries)
        assert best["value"] == "7.0"
        assert confidence > 0.9
        assert dist >= 0.0

    def test_far_colour_gives_low_confidence(self):
        entries = [
            {"value": "7.0", "unit": "", "rgb": [255, 180, 80], "hsv": [30, 175, 255], "risk_level": "neutral"},
        ]
        _, confidence, _ = match_colour_to_chart([0, 0, 0], entries)
        assert confidence < 0.3

    def test_selects_nearest_entry(self):
        entries = [
            {"value": "A", "unit": "", "rgb": [200, 100, 50], "hsv": [0, 0, 0], "risk_level": "low"},
            {"value": "B", "unit": "", "rgb": [50,  200, 50], "hsv": [0, 0, 0], "risk_level": "low"},
        ]
        best, _, _ = match_colour_to_chart([205, 105, 55], entries)
        assert best["value"] == "A"

    def test_returns_colour_distance(self):
        entries = [
            {"value": "7.0", "unit": "", "rgb": [255, 180, 80], "hsv": [30, 175, 255], "risk_level": "neutral"},
        ]
        _, _, dist = match_colour_to_chart([255, 180, 80], entries)
        assert dist == 0.0


class TestAnalyseTestStrip:
    def test_returns_strip_analysis_result(self):
        img = _solid_image(200, 150, 100, h=200, w=60)
        result = analyse_test_strip(img)
        assert isinstance(result, StripAnalysisResult)
        assert result.image_type == "test_strip"

    def test_includes_kit_id(self):
        img = _solid_image(200, 150, 100, h=200, w=60)
        result = analyse_test_strip(img)
        assert result.kit_id == "generic_16_in_1"

    def test_number_of_parameters_matches_chart(self):
        img = _solid_image(200, 150, 100, h=200, w=60)
        result = analyse_test_strip(img)
        assert len(result.parameters) == 7  # generic_16_in_1 has 7 params

    def test_parameters_have_risk_category(self):
        img = _solid_image(200, 150, 100, h=200, w=60)
        result = analyse_test_strip(img)
        for p in result.parameters:
            assert p.risk_category in ("boiling_resistant_warning", "treatment_required", "low", "neutral")

    def test_parameters_have_colour_distance(self):
        img = _solid_image(200, 150, 100, h=200, w=60)
        result = analyse_test_strip(img)
        for p in result.parameters:
            assert p.colour_distance >= 0.0

    def test_parameters_have_message(self):
        img = _solid_image(200, 150, 100, h=200, w=60)
        result = analyse_test_strip(img)
        for p in result.parameters:
            assert isinstance(p.message, str)

    def test_includes_all_four_safety_warnings(self):
        img = _solid_image(200, 150, 100, h=200, w=60)
        result = analyse_test_strip(img)
        warnings_text = " ".join(result.warnings)
        assert "does not replace laboratory testing" in warnings_text
        assert "Boiling does not remove" in warnings_text
        assert "every contaminant" in warnings_text
        assert "Water Quality Agent" in warnings_text

    def test_confidence_in_valid_range(self):
        img = _solid_image(200, 150, 100, h=200, w=60)
        result = analyse_test_strip(img)
        assert 0.0 <= result.overall_confidence <= 1.0
        for p in result.parameters:
            assert 0.0 <= p.confidence <= 1.0

    def test_image_quality_has_glare_warning_field(self):
        img = _solid_image(200, 150, 100, h=200, w=60)
        result = analyse_test_strip(img)
        assert hasattr(result.image_quality, "glare_warning")

    def test_boiling_resistant_risk_flags_is_list(self):
        img = _solid_image(200, 150, 100, h=200, w=60)
        result = analyse_test_strip(img)
        assert isinstance(result.boiling_resistant_risk_flags, list)
