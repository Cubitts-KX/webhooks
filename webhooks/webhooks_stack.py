from aws_cdk import (
    Stack,
)
from constructs import Construct


from webhooks.inbound_data.construct import InboundData
from webhooks.data_processors.shopify_sylius.construct import ShopifyToSyliusProcessor


class WebhooksStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        inbound_data = InboundData(self, "InboundData")

        ShopifyToSyliusProcessor(
            self, "ShopifyToSyliusProcessor", bucket=inbound_data.bucket
        )
