"""
Submission handler: orchestrates multi-image (1-3) CV analysis.
Routes each image to the appropriate processor based on declared or classified kit type.
Returns a SubmissionResult.
"""
import uuid
from pathlib import Path
from typing import Optional

import numpy as np

from .engine import analyse_test_strip, assess_image_quality, load_image
from .heavy_metals_processor import analyse_heavy_metals_strip
from .kit_classifier import classify_kit_bedrock, classify_kit_local
from .models import (
    CombinedBoilingRiskFlag,
    ImageResult,
    ImageQuality,
    SubmissionResult,
    TDSResult,
)
from .tds_processor import process_tds_bedrock, process_tds_local

_HM_CHART = Path(__file__).parent / "reference_charts" / "heavy_metals_strip.json"

_RISK_ORDER = {"caution": 0, "warning": 1, "critical": 2}


def _strip_to_image_result(strip_result, image_id: str, declared_kit_type: Optional[str]) -> ImageResult:
    classified = strip_result.kit_id
    mismatch = declared_kit_type is not None and declared_kit_type != classified
    has_issues = bool(strip_result.boiling_resistant_risk_flags) or bool(strip_result.warnings)
    status = "processed_with_warnings" if has_issues else "processed"
    return ImageResult(
        image_id=image_id,
        kit_type=classified,
        declared_kit_type=declared_kit_type,
        kit_type_mismatch=mismatch,
        processing_status=status,
        parameters=strip_result.parameters,
        boiling_resistant_risk_flags=strip_result.boiling_resistant_risk_flags,
        overall_confidence=strip_result.overall_confidence,
        image_quality=strip_result.image_quality,
        warnings=strip_result.warnings,
    )


def _tds_to_image_result(
    tds_result: TDSResult,
    image_id: str,
    declared_kit_type: Optional[str],
    quality: ImageQuality,
) -> ImageResult:
    status = "processed" if tds_result.status == "processed" else "processed_with_warnings"
    return ImageResult(
        image_id=image_id,
        kit_type="tds_meter",
        declared_kit_type=declared_kit_type,
        processing_status=status,
        tds_result=tds_result,
        overall_confidence=tds_result.confidence,
        image_quality=quality,
        warnings=[
            "This is an estimated reading from image analysis and does not replace laboratory testing.",
            "Boiling does not remove dissolved solids.",
            "Final safety guidance must be handled by the Water Quality Agent and Treatment Guidance Agent.",
        ],
    )


def _build_combined_flags(image_results: list[ImageResult]) -> list[CombinedBoilingRiskFlag]:
    seen: dict[str, CombinedBoilingRiskFlag] = {}
    for ir in image_results:
        for flag in ir.boiling_resistant_risk_flags:
            existing = seen.get(flag.parameter)
            existing_order = _RISK_ORDER.get(existing.risk_level, 0) if existing else -1
            if existing is None or _RISK_ORDER.get(flag.risk_level, 0) > existing_order:
                seen[flag.parameter] = CombinedBoilingRiskFlag(
                    parameter=flag.parameter,
                    risk_level=flag.risk_level,
                    source_image_id=ir.image_id,
                    reason=flag.reason,
                )
    return list(seen.values())


def process_submission(
    image_items: list[tuple[bytes, Optional[str]]],
    cv_provider: str = "local",
) -> SubmissionResult:
    """
    image_items: list of (image_bytes, declared_kit_type | None), max 3 items.
    cv_provider: "local" or "aws".
    """
    submission_id = str(uuid.uuid4())
    image_results: list[ImageResult] = []
    processed_count = 0
    failed_count = 0

    classify_fn = classify_kit_bedrock if cv_provider == "aws" else classify_kit_local
    tds_fn = process_tds_bedrock if cv_provider == "aws" else process_tds_local

    for raw_bytes, declared_kit_type in image_items[:3]:
        image_id = str(uuid.uuid4())

        try:
            img = load_image(raw_bytes)
        except Exception as exc:
            image_results.append(ImageResult(
                image_id=image_id,
                kit_type="unknown",
                declared_kit_type=declared_kit_type,
                processing_status="error",
                warnings=[f"Could not decode image: {exc}"],
            ))
            failed_count += 1
            continue

        # Determine kit type
        if declared_kit_type and declared_kit_type != "unknown":
            kit_type = declared_kit_type
        else:
            source = raw_bytes if cv_provider == "aws" else img
            kit_type, _ = classify_fn(source)

        try:
            if kit_type == "tds_meter":
                tds_result = tds_fn(raw_bytes)
                quality = assess_image_quality(img)
                ir = _tds_to_image_result(tds_result, image_id, declared_kit_type, quality)

            elif kit_type == "heavy_metals_strip":
                if cv_provider == "aws":
                    from .aws_provider import analyse_test_strip_bedrock
                    strip = analyse_test_strip_bedrock(raw_bytes, chart_path=_HM_CHART)
                else:
                    strip = analyse_heavy_metals_strip(img)
                ir = _strip_to_image_result(strip, image_id, declared_kit_type)

            else:
                # generic_16_in_1 or unknown → treat as generic strip
                if cv_provider == "aws":
                    from .aws_provider import analyse_test_strip_bedrock
                    strip = analyse_test_strip_bedrock(raw_bytes)
                else:
                    strip = analyse_test_strip(img)
                ir = _strip_to_image_result(strip, image_id, declared_kit_type)

            image_results.append(ir)
            processed_count += 1

        except Exception as exc:
            image_results.append(ImageResult(
                image_id=image_id,
                kit_type=kit_type,
                declared_kit_type=declared_kit_type,
                processing_status="error",
                warnings=[f"Processing error: {exc}"],
            ))
            failed_count += 1

    if processed_count == 0:
        overall_status = "failed"
    elif failed_count > 0:
        overall_status = "partial"
    elif any(ir.processing_status == "processed_with_warnings" for ir in image_results):
        overall_status = "processed_with_warnings"
    else:
        overall_status = "processed"

    combined_flags = _build_combined_flags(image_results)

    return SubmissionResult(
        submission_id=submission_id,
        status=overall_status,
        images_processed=processed_count,
        results=image_results,
        combined_boiling_resistant_risk_flags=combined_flags,
    )
