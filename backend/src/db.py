"""
DynamoDB client for storing and retrieving CV submission results.
Table: waterforall-cv-submissions (partition key: submission_id, String)
Storage is best-effort — the CV pipeline never fails due to DB unavailability.
"""
import json
import os
from typing import Optional

_TABLE_NAME = os.getenv("DYNAMODB_TABLE", "waterforall-cv-submissions")
_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")


def _table():
    import boto3
    dynamodb = boto3.resource("dynamodb", region_name=_REGION)
    return dynamodb.Table(_TABLE_NAME)


def save_submission(submission_id: str, result_dict: dict) -> None:
    """Persist a submission result. Silently skips on any error."""
    try:
        _table().put_item(Item={
            "submission_id": submission_id,
            "result": json.dumps(result_dict),
        })
    except Exception:
        pass


def get_submission(submission_id: str) -> Optional[dict]:
    """Retrieve a stored submission result by ID. Returns None if not found."""
    try:
        from botocore.exceptions import ClientError
        resp = _table().get_item(Key={"submission_id": submission_id})
        item = resp.get("Item")
        if item:
            return json.loads(item["result"])
        return None
    except Exception:
        return None
