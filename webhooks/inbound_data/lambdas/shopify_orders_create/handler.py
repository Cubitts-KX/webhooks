import os
import json
import boto3


s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]


def store_body(event, _):
    request_body = json.loads(event["body"])
    key = generate_key(request_body)

    s3.put_object(Body=json.dumps(request_body), Bucket=BUCKET_NAME, Key=key)

    return {"statusCode": 201}


def generate_key(post_body):
    path = "shopify/orders/create"
    file = post_body["id"]

    return f"{path}/{file}.json"
