import json
import boto3
import urllib.request

s3_client = boto3.client("s3")


def handler(event, context):
    print(event)
    for record in event["Records"]:
        message_body = json.loads(record["body"])

        s3_key = message_body["detail"]["object"]["key"]
        bucket_name = message_body["detail"]["bucket"]["name"]

        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        data = response["Body"].read()

        url = "https://staging.cubittsadmin.com/sync/order/webhook/create"
        req = urllib.request.Request(url)
        req.add_header("Content-Type", "application/json")

        # URLLib will throw an error here if the response is not successful
        response = urllib.request.urlopen(req, data)

    return {"statusCode": 200, "body": f"Data processed successfully for {bucket_name}/{s3_key}"}
