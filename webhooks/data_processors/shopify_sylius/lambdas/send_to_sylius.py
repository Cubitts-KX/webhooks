import json
import os
import urllib.request

import boto3

s3_client = boto3.client("s3")


def handler(event, context):
    for record in event["Records"]:
        message_body = json.loads(record["body"])

        s3_key = message_body["detail"]["object"]["key"]
        bucket_name = message_body["detail"]["bucket"]["name"]

        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        data = response["Body"].read()

        json_data = json.loads(data)
        body = json_data["body"]

        url = build_url()
        req = urllib.request.Request(url)
        req.add_header("Content-Type", "application/json")

        # URLLib will throw an error here if the response is not successful
        response = urllib.request.urlopen(req, json.dumps(body).encode("utf-8"))

    return {
        "statusCode": 200,
        "body": f"Data processed successfully for {bucket_name}/{s3_key}",
    }


def build_url():
    cubitts_env = os.environ["CUBITTS_ENV"]
    subdomain = "www" if cubitts_env == "production" else "staging"
    base_url = f"https://{subdomain}.cubittsadmin.com/sync"

    prefix = os.environ["PREFIX"]
    _, resource, action = prefix.split("/")

    path = f"/{resource}/webhook/{action}"
    return f"{base_url}{path}"
