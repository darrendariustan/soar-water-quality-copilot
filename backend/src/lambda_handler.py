"""
AWS Lambda entry point.
Triggered by S3 ObjectCreated events on the raw/ prefix.
Downloads the image, runs CV analysis, and returns the result JSON.
Storage to RDS is handled by the backend API layer (out of scope for CV module).
"""
import json
import os

import boto3

from .cv.engine import analyse_test_strip, load_image
from .cv.classifier import classify_water_sample

_s3 = boto3.client("s3")


def handler(event: dict, context) -> dict:
    # Support both direct invocation and S3 event trigger
    if "Records" in event:
        record = event["Records"][0]["s3"]
        bucket = record["bucket"]["name"]
        key = record["object"]["key"]
        image_type = "test_strip" if "test-strips" in key else "water_sample"
    else:
        bucket = event.get("bucket")
        key = event.get("key")
        image_type = event.get("image_type", "test_strip")

    if not bucket or not key:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing bucket or key"})}

    try:
        response = _s3.get_object(Bucket=bucket, Key=key)
        image_bytes = response["Body"].read()
        img = load_image(image_bytes)

        if image_type == "water_sample":
            result = classify_water_sample(img)
        else:
            result = analyse_test_strip(img)

        return {
            "statusCode": 200,
            "body": json.dumps(result.model_dump()),
            "headers": {"Content-Type": "application/json"},
        }
    except Exception as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(exc)}),
        }
