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

        scan_bucket_name = os.environ["SCAN_BUCKET_NAME"]

        scans = body["scans"]
        for scan in scans:
            scan_id = scan["id"]

            scan_files = scan["reconstruction3D"]
            for ext in ["obj", "png", "mtl"]:
                copy_to_s3(
                    scan_files[f"{ext}Url"],
                    scan_bucket_name,
                    f"myfit/{scan_id}/head3d.{['obj', 'png', 'mtl']}",
                )

        url = build_url()
        req = urllib.request.Request(url)
        req.add_header("Content-Type", "application/json")
        response = urllib.request.urlopen(req, json.dumps(body).encode("utf-8"))

    return {
        "statusCode": 200,
        "body": f"Data processed successfully for {bucket_name}/{s3_key}",
    }


def copy_to_s3(url, bucket_name, key_name):
    response = urllib.request.urlopen(url)
    s3_client.put_object(Body=response, Bucket=bucket_name, Key=key_name)


def build_url():
    cubitts_env = os.environ["CUBITTS_ENV"]
    subdomain = "www" if cubitts_env == "production" else "staging"
    base_url = f"https://{subdomain}.cubittsadmin.com"

    path = "/api/myfit/scan"
    return f"{base_url}{path}"
