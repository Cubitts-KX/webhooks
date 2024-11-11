import json
import os
import time

import boto3

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]


def store_body(event, _):
    print(event)
    path = event["rawPath"]

    headers = event["headers"]
    request_body = json.loads(event["body"])

    key = generate_key(path, request_body)
    stored_content = {"headers": headers, "body": request_body}
    s3.put_object(Body=json.dumps(stored_content), Bucket=BUCKET_NAME, Key=key)

    return {"statusCode": 201}


def generate_key(path, post_body):
    no_leading_slashes = path.strip("/")
    id = post_body["id"]
    timestamp = int(time.time())

    return f"{no_leading_slashes}/{id}-{timestamp}.json"
