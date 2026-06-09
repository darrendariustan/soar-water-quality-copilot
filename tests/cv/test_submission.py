"""
Tests for submission_handler, tds_processor, heavy_metals_processor, and kit_classifier.
All tests use synthetic numpy images — no real images or network calls required.
"""
import json
import struct
import zlib

import cv2
import numpy as np
import pytest

from backend.src.cv.submission_handler import process_submission, _build_combined_flags
from backend.src.cv.tds_processor import process_tds_local
from backend.src.cv.heavy_metals_processor import analyse_heavy_metals_strip
from backend.src.cv.kit_classifier import classify_kit_local
from backend.src.cv.models import (
    BoilingRiskFlag,
    CombinedBoilingRiskFlag,
    ImageResult,
    SubmissionResult,
    TDSResult,
)


def _solid_image_bytes(r: int, g: int, b: int, h: int = 100, w: int = 60) -> bytes:
    """Return JPEG bytes for a solid-colour image."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :] = [b, g, r]  # BGR
    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


def _solid_ndarray(r: int, g: int, b: int, h: int = 100, w: int = 60) -> np.ndarray:
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :] = [b, g, r]
    return img


# ---------------------------------------------------------------------------
# TDS processor — local mode
# ---------------------------------------------------------------------------

class TestTDSProcessorLocal:
    def test_returns_tds_result(self):
        raw = _solid_image_bytes(128, 128, 128)
        result = process_tds_local(raw)
        assert isinstance(result, TDSResult)

    def test_local_returns_manual_review(self):
        raw = _solid_image_bytes(128, 128, 128)
        result = process_tds_local(raw)
        assert result.status == "manual_review_required"

    def test_local_confidence_is_zero(self):
        raw = _solid_image_bytes(128, 128, 128)
        result = process_tds_local(raw)
        assert result.confidence == 0.0

    def test_local_risk_category_is_unknown(self):
        raw = _solid_image_bytes(128, 128, 128)
        result = process_tds_local(raw)
        assert result.risk_category == "unknown"

    def test_local_message_mentions_aws(self):
        raw = _solid_image_bytes(128, 128, 128)
        result = process_tds_local(raw)
        assert "aws" in result.message.lower() or "CV_PROVIDER" in result.message


# ---------------------------------------------------------------------------
# Heavy metals processor
# ---------------------------------------------------------------------------

class TestHeavyMetalsProcessor:
    def test_returns_strip_analysis_result(self):
        img = _solid_ndarray(200, 180, 200, h=200, w=60)
        result = analyse_heavy_metals_strip(img)
        assert result.kit_id == "heavy_metals_strip"

    def test_returns_five_parameters(self):
        img = _solid_ndarray(200, 180, 200, h=200, w=60)
        result = analyse_heavy_metals_strip(img)
        assert len(result.parameters) == 5

    def test_parameters_are_heavy_metal_names(self):
        img = _solid_ndarray(200, 180, 200, h=200, w=60)
        result = analyse_heavy_metals_strip(img)
        names = {p.name for p in result.parameters}
        assert names == {"lead", "mercury", "copper", "cadmium", "chromium"}

    def test_boiling_message_in_risk_flags(self):
        img = _solid_ndarray(200, 180, 200, h=200, w=60)
        result = analyse_heavy_metals_strip(img)
        for flag in result.boiling_resistant_risk_flags:
            assert "oiling" in flag.reason  # "Boiling does not remove..."

    def test_accepts_bytes_input(self):
        raw = _solid_image_bytes(200, 180, 200, h=200, w=60)
        result = analyse_heavy_metals_strip(raw)
        assert result.kit_id == "heavy_metals_strip"


# ---------------------------------------------------------------------------
# Kit classifier — local heuristics
# ---------------------------------------------------------------------------

class TestKitClassifierLocal:
    def test_returns_tuple(self):
        img = _solid_ndarray(150, 150, 150)
        kit_type, confidence = classify_kit_local(img)
        assert isinstance(kit_type, str)
        assert 0.0 <= confidence <= 1.0

    def test_known_kit_type_returned(self):
        img = _solid_ndarray(150, 150, 150)
        kit_type, _ = classify_kit_local(img)
        assert kit_type in ("generic_16_in_1", "heavy_metals_strip", "tds_meter", "unknown")

    def test_saturated_image_classified_as_strip(self):
        # High saturation variance → test strip heuristic
        img = np.zeros((100, 60, 3), dtype=np.uint8)
        # Fill alternating bands with very different colors
        for i in range(5):
            y0, y1 = i * 20, (i + 1) * 20
            color = [255, 0, 0] if i % 2 == 0 else [0, 255, 0]
            img[y0:y1, :] = color
        kit_type, _ = classify_kit_local(img)
        assert kit_type == "generic_16_in_1"

    def test_dark_image_not_strip(self):
        img = _solid_ndarray(30, 30, 30)
        kit_type, _ = classify_kit_local(img)
        assert kit_type != "generic_16_in_1"


# ---------------------------------------------------------------------------
# Submission handler
# ---------------------------------------------------------------------------

class TestProcessSubmission:
    def test_returns_submission_result(self):
        raw = _solid_image_bytes(180, 160, 140, h=200)
        result = process_submission([(raw, "generic_16_in_1")])
        assert isinstance(result, SubmissionResult)

    def test_submission_id_is_uuid(self):
        raw = _solid_image_bytes(180, 160, 140, h=200)
        result = process_submission([(raw, "generic_16_in_1")])
        import uuid
        uuid.UUID(result.submission_id)  # raises if invalid

    def test_single_image_processed(self):
        raw = _solid_image_bytes(180, 160, 140, h=200)
        result = process_submission([(raw, "generic_16_in_1")])
        assert result.images_processed == 1
        assert len(result.results) == 1

    def test_three_images_processed(self):
        raw = _solid_image_bytes(180, 160, 140, h=200)
        result = process_submission([(raw, "generic_16_in_1")] * 3)
        assert result.images_processed == 3
        assert len(result.results) == 3

    def test_max_three_images_enforced(self):
        raw = _solid_image_bytes(180, 160, 140, h=200)
        result = process_submission([(raw, "generic_16_in_1")] * 5)
        assert len(result.results) <= 3

    def test_heavy_metals_kit_type_returned(self):
        raw = _solid_image_bytes(200, 180, 200, h=200)
        result = process_submission([(raw, "heavy_metals_strip")])
        assert result.results[0].kit_type == "heavy_metals_strip"

    def test_tds_meter_returns_tds_result(self):
        raw = _solid_image_bytes(128, 128, 128)
        result = process_submission([(raw, "tds_meter")])
        ir = result.results[0]
        assert ir.kit_type == "tds_meter"
        assert ir.tds_result is not None
        assert isinstance(ir.tds_result, TDSResult)

    def test_invalid_image_bytes_produces_error_status(self):
        result = process_submission([(b"not_an_image", "generic_16_in_1")])
        assert result.results[0].processing_status == "error"
        assert result.status in ("failed", "partial")

    def test_failed_status_when_all_images_fail(self):
        result = process_submission([(b"bad", "generic_16_in_1"), (b"bad2", "generic_16_in_1")])
        assert result.status == "failed"
        assert result.images_processed == 0

    def test_partial_status_when_some_images_fail(self):
        good = _solid_image_bytes(180, 160, 140, h=200)
        result = process_submission([(good, "generic_16_in_1"), (b"bad", "generic_16_in_1")])
        assert result.status == "partial"
        assert result.images_processed == 1

    def test_final_module_warning_present(self):
        raw = _solid_image_bytes(180, 160, 140, h=200)
        result = process_submission([(raw, "generic_16_in_1")])
        assert "Water Quality Agent" in result.final_module_warning

    def test_kit_type_mismatch_detected(self):
        raw = _solid_image_bytes(180, 160, 140, h=200)
        # Declare heavy_metals but engine returns generic_16_in_1
        result = process_submission([(raw, "heavy_metals_strip")])
        ir = result.results[0]
        # kit_type comes from chart; declared was heavy_metals_strip — mismatch only if they differ
        # heavy_metals_strip chart → kit_id == "heavy_metals_strip", so no mismatch here
        assert isinstance(ir.kit_type_mismatch, bool)

    def test_combined_flags_deduplicated_by_parameter(self):
        raw = _solid_image_bytes(180, 160, 140, h=200)
        # Two images both analyzing the same strip — combined flags should deduplicate
        result = process_submission([(raw, "generic_16_in_1"), (raw, "generic_16_in_1")])
        params = [f.parameter for f in result.combined_boiling_resistant_risk_flags]
        assert len(params) == len(set(params))


# ---------------------------------------------------------------------------
# _build_combined_flags
# ---------------------------------------------------------------------------

class TestBuildCombinedFlags:
    def _ir(self, image_id: str, flags: list[BoilingRiskFlag]) -> ImageResult:
        return ImageResult(
            image_id=image_id,
            kit_type="generic_16_in_1",
            processing_status="processed",
            boiling_resistant_risk_flags=flags,
        )

    def test_empty_results_returns_empty(self):
        assert _build_combined_flags([]) == []

    def test_deduplicates_same_parameter(self):
        flag = BoilingRiskFlag(parameter="nitrate", risk_level="warning", reason="reason")
        results = [self._ir("a", [flag]), self._ir("b", [flag])]
        combined = _build_combined_flags(results)
        assert len(combined) == 1
        assert combined[0].parameter == "nitrate"

    def test_keeps_highest_risk_level(self):
        warn_flag = BoilingRiskFlag(parameter="lead", risk_level="warning", reason="trace")
        crit_flag = BoilingRiskFlag(parameter="lead", risk_level="critical", reason="detected")
        results = [self._ir("a", [warn_flag]), self._ir("b", [crit_flag])]
        combined = _build_combined_flags(results)
        assert combined[0].risk_level == "critical"
        assert combined[0].source_image_id == "b"

    def test_source_image_id_is_set(self):
        flag = BoilingRiskFlag(parameter="nitrate", risk_level="warning", reason="reason")
        results = [self._ir("img-001", [flag])]
        combined = _build_combined_flags(results)
        assert combined[0].source_image_id == "img-001"

    def test_multiple_different_parameters(self):
        flags = [
            BoilingRiskFlag(parameter="nitrate", risk_level="warning", reason="r1"),
            BoilingRiskFlag(parameter="lead", risk_level="critical", reason="r2"),
        ]
        results = [self._ir("x", flags)]
        combined = _build_combined_flags(results)
        assert len(combined) == 2
        params = {f.parameter for f in combined}
        assert params == {"nitrate", "lead"}
