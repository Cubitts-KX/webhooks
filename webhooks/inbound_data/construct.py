from aws_cdk import (
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
    aws_lambda as lambda_,
    aws_s3 as s3,
)

from constructs import Construct


class InboundData(Construct):
    def __init__(self, scope: Construct, id: str, cubitts_env: str, **kwargs) -> None:
        super().__init__(scope, id)

        api = apigw.HttpApi(
            self,
            "InboundWebhookDataAPI",
        )

        bucket = s3.Bucket(
            self,
            "InboundWebhookDataBucket",
            event_bridge_enabled=True,
            versioned=True,
        )
        self.bucket = bucket

        shopify_order_create_lambda_fn = lambda_.Function(
            self,
            "ShopifyOrdersCreateFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.store_body",
            code=lambda_.Code.from_asset(
                "webhooks/inbound_data/lambdas/shopify_orders_create"
            ),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "CUBITTS_ENV": cubitts_env,
            },
        )
        bucket.grant_write(shopify_order_create_lambda_fn)

        # Create the route
        api.add_routes(
            path="/shopify/orders/create",
            methods=[apigw.HttpMethod.POST],
            integration=integrations.HttpLambdaIntegration(
                "ShopifyOrderCreateIntegration", shopify_order_create_lambda_fn
            ),
        )
