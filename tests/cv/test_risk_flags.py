import json
import numpy as np
import pytest
from pathlib import Path

from backend.src.cv.engine import analyse_test_strip, _risk_level_to_category


class TestRiskLevelToCategory:
    def test_critical_always_treatment_required(self):
        assert _risk_level_to_category("critical", "nitrate") == "treatment_required"

    def test_warning_on_boiling_resistant_param(self):
        assert _risk_level_to_category("warning", "nitrate") == "boiling_resistant_warning"
        assert _risk_level_to_category("warning", "nitrite") == "boiling_resistant_warning"
        assert _risk_level_to_category("warning", "iron") == "boiling_resistant_warning"

    def test_warning_on_non_boiling_resistant_param(self):
        assert _risk_level_to_category("warning", "pH") == "treatment_required"

    def test_low_passes_through(self):
        assert _risk_level_to_category("low", "hardness") == "low"

    def test_neutral_passes_through(self):
        assert _risk_level_to_category("neutral", "pH") == "neutral"


class TestBoilingRiskFlags:
    def _make_image(self, h: int = 200, w: int = 60) -> np.ndarray:
        return np.full((h, w, 3), 150, dtype=np.uint8)

    def test_risk_flags_is_list(self):
        result = analyse_test_strip(self._make_image())
        assert isinstance(result.boiling_resistant_risk_flags, list)

    def test_risk_flag_fields(self):
        result = analyse_test_strip(self._make_image())
        for flag in result.boiling_resistant_risk_flags:
            assert flag.parameter
            assert flag.risk_level in ("warning", "critical")
            assert flag.reason

    def test_custom_chart_no_risk_levels_produces_no_flags(self, tmp_path):
        chart = {
            "kit_id": "test_kit",
            "kit_name": "Test",
            "parameters": {
                "pH": [
                    {"value": "7.0", "unit": "", "rgb": [200, 200, 200], "hsv": [0, 0, 200], "risk_level": "low"}
                ]
            }
        }
        chart_file = tmp_path / "test_chart.json"
        chart_file.write_text(json.dumps(chart))
        img = np.full((100, 50, 3), 200, dtype=np.uint8)
        result = analyse_test_strip(img, chart_path=chart_file)
        assert result.boiling_resistant_risk_flags == []

    def test_custom_chart_warning_produces_flag(self, tmp_path):
        chart = {
            "kit_id": "test_kit",
            "kit_name": "Test",
            "parameters": {
                "nitrate": [
                    {"value": "50", "unit": "mg/L", "rgb": [200, 200, 200], "hsv": [0, 0, 200], "risk_level": "warning"}
                ]
            }
        }
        chart_file = tmp_path / "test_chart.json"
        chart_file.write_text(json.dumps(chart))
        img = np.full((100, 50, 3), 200, dtype=np.uint8)
        result = analyse_test_strip(img, chart_path=chart_file)
        assert len(result.boiling_resistant_risk_flags) == 1
        assert result.boiling_resistant_risk_flags[0].parameter == "nitrate"
        assert result.boiling_resistant_risk_flags[0].risk_level == "warning"
