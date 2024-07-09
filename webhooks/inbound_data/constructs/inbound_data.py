from aws_cdk import aws_apigatewayv2, aws_s3
from constructs import Construct

from webhooks.inbound_data.constructs.shopify import (
    ShopifyInbound,
    ShopifyInboundOptions,
)


class InboundData(Construct):
    def __init__(self, scope: Construct, id: str, cubitts_env: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = aws_apigatewayv2.HttpApi(
            self,
            "InboundWebhookDataAPI",
        )

        bucket = aws_s3.Bucket(
            self,
            "InboundWebhookDataBucket",
            event_bridge_enabled=True,
            versioned=True,
        )
        self.bucket = bucket

        ShopifyInbound(
            self,
            "ShopifyInboundWebhooks",
            options=ShopifyInboundOptions(
                bucket=bucket,
                api=api,
            ),
            cubitts_env=cubitts_env,
        )
