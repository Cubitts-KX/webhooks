from aws_cdk import (
    Stack,
)
from constructs import Construct

from webhooks.data_processors.myfit_sylius.constructs.scan_finished import (
    MyFitToSyliusFinishedScanProcessor,
    MyFitToSyliusFinishedScanProcessorOptions,
)
from webhooks.data_processors.shopify_sylius.constructs.processors import (
    ShopifyToSyliusProcessors,
)
from webhooks.inbound_data.constructs.inbound_data import InboundData


class WebhooksStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, cubitts_env: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Shopify and MyFit share the same inboudn data processing as both do the same thing
        # of storing the body of the request in S3
        inbound_data = InboundData(self, "InboundData", cubitts_env=cubitts_env)

        # Data Processors are unique to each integrated service
        ShopifyToSyliusProcessors(
            self,
            "ShopifyToSyliusProcessors",
            bucket=inbound_data.bucket,
            cubitts_env=cubitts_env,
        )

        MyFitToSyliusFinishedScanProcessor(
            self,
            "MyFitToSyliusFinishedProcessor",
            MyFitToSyliusFinishedScanProcessorOptions(
                bucket=inbound_data.bucket,
                prefix="myfit/scan/finished",
                handler="copy_to_s3.handler",
            ),
            cubitts_env=cubitts_env,
        )
