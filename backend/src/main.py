import json
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .cv.engine import analyse_test_strip, load_image
from .cv.classifier import classify_water_sample
from .cv.submission_handler import process_submission

_STATIC_DIR = Path(__file__).parent / "static"
_CV_PROVIDER = os.getenv("CV_PROVIDER", "local")
_S3_BUCKET = os.getenv("S3_BUCKET", "waterforall-dev-cv-images")
_S3_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

app = FastAPI(title="WaterForAll CV API", version="0.2.0")
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(str(_STATIC_DIR / "index.html"))


# ---------------------------------------------------------------------------
# Legacy single-image endpoints (kept for backward compatibility)
# ---------------------------------------------------------------------------

@app.post("/analyze/test-strip")
async def analyze_test_strip_endpoint(file: UploadFile = File(...)):
    raw = await file.read()
    try:
        if _CV_PROVIDER == "aws":
            from .cv.aws_provider import analyse_test_strip_rekognition
            result = analyse_test_strip_rekognition(raw)
        else:
            img = load_image(raw)
            result = analyse_test_strip(img)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return JSONResponse(result.model_dump())


@app.post("/analyze/water-sample")
async def analyze_water_sample_endpoint(file: UploadFile = File(...)):
    raw = await file.read()
    try:
        if _CV_PROVIDER == "aws":
            from .cv.aws_provider import classify_water_sample_rekognition
            result = classify_water_sample_rekognition(raw)
        else:
            img = load_image(raw)
            result = classify_water_sample(img)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return JSONResponse(result.model_dump())


# ---------------------------------------------------------------------------
# Multi-image submission endpoint
# ---------------------------------------------------------------------------

@app.post("/cv/submissions")
async def create_submission(
    files: list[UploadFile] = File(...),
    kit_types: Optional[str] = Form(None),
):
    """
    Accept 1–3 image files and process them as a single submission.

    kit_types (optional form field): JSON array of kit type strings, one per file.
    e.g. '["generic_16_in_1", null, "tds_meter"]'
    Valid values: "generic_16_in_1", "heavy_metals_strip", "tds_meter", null (auto-detect).
    """
    if not files or len(files) > 3:
        raise HTTPException(status_code=422, detail="Submit between 1 and 3 image files.")

    declared_types: list[Optional[str]] = [None] * len(files)
    if kit_types:
        try:
            parsed = json.loads(kit_types)
            if not isinstance(parsed, list):
                raise ValueError
            for i, v in enumerate(parsed[:len(files)]):
                declared_types[i] = v if isinstance(v, str) else None
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="kit_types must be a JSON array of strings or nulls.")

    image_items: list[tuple[bytes, Optional[str]]] = []
    for upload, kit_type in zip(files, declared_types):
        raw = await upload.read()
        image_items.append((raw, kit_type))

    result = process_submission(image_items, cv_provider=_CV_PROVIDER)

    # Best-effort persistence to DynamoDB
    if _CV_PROVIDER == "aws":
        try:
            from .db import save_submission
            save_submission(result.submission_id, result.model_dump())
        except Exception:
            pass

    return JSONResponse(result.model_dump())


# ---------------------------------------------------------------------------
# Pre-signed S3 upload URL (AWS mode only)
# ---------------------------------------------------------------------------

@app.post("/cv/upload-url")
async def get_upload_url(kit_type: Optional[str] = Form(None)):
    """
    Generate a pre-signed S3 PUT URL for direct browser → S3 upload.
    Returns {upload_url, s3_key, result_id}.
    Only functional when CV_PROVIDER=aws and S3 bucket is configured.
    """
    if _CV_PROVIDER != "aws":
        raise HTTPException(
            status_code=503,
            detail="Pre-signed URLs are only available in AWS mode (CV_PROVIDER=aws).",
        )
    try:
        import boto3
        s3 = boto3.client("s3", region_name=_S3_REGION)
        result_id = str(uuid.uuid4())
        prefix = kit_type or "unknown"
        s3_key = f"raw/{prefix}/{result_id}.jpg"
        upload_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": _S3_BUCKET, "Key": s3_key, "ContentType": "image/jpeg"},
            ExpiresIn=900,  # 15 minutes
        )
        return JSONResponse({"upload_url": upload_url, "s3_key": s3_key, "result_id": result_id})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not generate upload URL: {exc}")


# ---------------------------------------------------------------------------
# Retrieve stored submission result
# ---------------------------------------------------------------------------

@app.get("/cv/results/{submission_id}")
async def get_result(submission_id: str):
    """Retrieve a previously stored submission result from DynamoDB."""
    try:
        from .db import get_submission
        result = get_submission(submission_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Storage unavailable: {exc}")

    if result is None:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return JSONResponse(result)
