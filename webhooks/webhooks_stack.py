from aws_cdk import (
    Stack,
)
from constructs import Construct

from webhooks.data_processors.shopify_sylius.constructs.processors import (
    ShopifyToSyliusProcessors,
)
from webhooks.inbound_data.constructs.inbound_data import InboundData


class WebhooksStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, cubitts_env: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        inbound_data = InboundData(self, "InboundData", cubitts_env=cubitts_env)

        # Data Processors
        ShopifyToSyliusProcessors(
            self,
            "ShopifyToSyliusProcessors",
            bucket=inbound_data.bucket,
            cubitts_env=cubitts_env,
        )
