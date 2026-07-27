"""Reference AWS Lambda transformation handler for the FlowPilot portfolio.

The deployed portfolio uses checked-in synthetic data. This handler demonstrates how an
S3 event can validate a CSV object and write a normalized Parquet object to a curated prefix.
"""
from __future__ import annotations

import io
import os
from urllib.parse import unquote_plus

import boto3
import pandas as pd

s3 = boto3.client("s3")
CURATED_PREFIX = os.getenv("CURATED_PREFIX", "curated")


def lambda_handler(event, context):
    processed = []
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])
        if not key.lower().endswith(".csv"):
            continue
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        frame = pd.read_csv(io.BytesIO(body))
        frame.columns = [c.strip().lower().replace(" ", "_") for c in frame.columns]
        if frame.empty:
            raise ValueError(f"{key} contains no rows")
        output = io.BytesIO()
        frame.to_parquet(output, index=False)
        output_key = f"{CURATED_PREFIX}/{key.rsplit('/', 1)[-1].rsplit('.', 1)[0]}.parquet"
        s3.put_object(Bucket=bucket, Key=output_key, Body=output.getvalue())
        processed.append({"source": key, "output": output_key, "rows": len(frame)})
    return {"statusCode": 200, "processed": processed}
