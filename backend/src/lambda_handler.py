"""
AWS Lambda entry point.
Triggered by S3 ObjectCreated events on the raw/ prefix.
S3 key format: raw/{kit_type}/{uuid}.jpg
  e.g. raw/generic_16_in_1/abc123.jpg
       raw/heavy_metals_strip/def456.jpg
       raw/tds_meter/ghi789.jpg
"""
import json
import os

import boto3

from .cv.submission_handler import process_submission
from .db import save_submission

_s3 = boto3.client("s3")
_CV_PROVIDER = os.getenv("CV_PROVIDER", "aws")

_KIT_TYPES = {"generic_16_in_1", "heavy_metals_strip", "tds_meter"}


def _kit_from_key(key: str) -> str | None:
    """Extract kit type from S3 key prefix: raw/{kit_type}/filename."""
    parts = key.split("/")
    if len(parts) >= 2 and parts[1] in _KIT_TYPES:
        return parts[1]
    return None


def handler(event: dict, context) -> dict:
    if "Records" in event:
        record = event["Records"][0]["s3"]
        bucket = record["bucket"]["name"]
        key = record["object"]["key"]
    else:
        bucket = event.get("bucket")
        key = event.get("key")

    if not bucket or not key:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing bucket or key"})}

    try:
        resp = _s3.get_object(Bucket=bucket, Key=key)
        image_bytes = resp["Body"].read()
    except Exception as exc:
        return {"statusCode": 500, "body": json.dumps({"error": f"S3 read failed: {exc}"})}

    declared_kit_type = _kit_from_key(key)
    result = process_submission([(image_bytes, declared_kit_type)], cv_provider=_CV_PROVIDER)

    save_submission(result.submission_id, result.model_dump())

    return {
        "statusCode": 200,
        "body": json.dumps(result.model_dump()),
        "headers": {"Content-Type": "application/json"},
    }
