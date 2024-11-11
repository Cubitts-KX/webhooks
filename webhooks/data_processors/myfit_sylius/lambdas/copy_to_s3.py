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
            copy_to_s3(scan_files["objUrl"], scan_bucket_name, f"{scan_id}/head3d.obj")
            copy_to_s3(scan_files["pngUrl"], scan_bucket_name, f"{scan_id}/texture.png")

    return {
        "statusCode": 200,
        "body": f"Data processed successfully for {bucket_name}/{s3_key}",
    }


def copy_to_s3(url, bucket_name, key_name):
    response = urllib.request.urlopen(url)
    s3_client.put_object(Body=response, Bucket=bucket_name, Key=key_name)
