from aws_cdk import aws_s3
from constructs import Construct

from webhooks.data_processors.shopify_sylius.constructs.base_processor import (
    ShopifyToSyliusProcessor,
    ShopifyToSyliusProcessorOptions,
)
from webhooks.utils import route_to_name


class ShopifyToSyliusProcessors(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        bucket: aws_s3.Bucket,
        cubitts_env: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        shopify_prefixes = [
            "shopify/order/create",
            "shopify/order/update",
            "shopify/product/update",
            "shopify/customer/create",
            "shopify/customer/update",
        ]

        for prefix in shopify_prefixes:
            name = route_to_name(prefix)

            ShopifyToSyliusProcessor(
                self,
                f"{name}ToSyliusProcessor",
                options=ShopifyToSyliusProcessorOptions(
                    prefix=prefix,
                    handler="send_to_sylius.handler",
                    bucket=bucket,
                ),
                cubitts_env=cubitts_env,
            )
