from aws_cdk import (
    Stack,
)
from constructs import Construct


from webhooks.inbound_data.construct import InboundData
from webhooks.data_processors.shopify_sylius.construct import (
    ShopifyToSyliusProcessor,
    ShopifyToSyliusProcessorOptions,
)


class WebhooksStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, cubitts_env: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        inbound_data = InboundData(self, "InboundData", cubitts_env=cubitts_env)

        ShopifyToSyliusProcessor(
            self,
            "ShopifyOrderCreateToSyliusProcessor",
            options=ShopifyToSyliusProcessorOptions(
                prefix="shopify/orders/create",
                handler="send_to_sylius.order_create",
                bucket=inbound_data.bucket,
            ),
            cubitts_env=cubitts_env,
        )

        ShopifyToSyliusProcessor(
            self,
            "ShopifyOrderUpdateToSyliusProcessor",
            options=ShopifyToSyliusProcessorOptions(
                prefix="shopify/orders/update",
                handler="send_to_sylius.order_create",
                bucket=inbound_data.bucket,
            ),
            cubitts_env=cubitts_env,
        )
