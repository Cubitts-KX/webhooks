from dataclasses import dataclass

from aws_cdk import aws_apigatewayv2, aws_apigatewayv2_integrations, aws_lambda, aws_s3
from constructs import Construct

from webhooks.utils import route_to_name


@dataclass
class ShopifyInboundOptions:
    bucket: aws_s3.Bucket
    api: aws_apigatewayv2.HttpApi


class ShopifyInbound(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        options: ShopifyInboundOptions,
        cubitts_env: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        shopify_inbound_fn = aws_lambda.Function(
            self,
            "Function",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            handler="shopify.store_body",
            code=aws_lambda.Code.from_asset("webhooks/inbound_data/lambdas"),
            environment={
                "BUCKET_NAME": options.bucket.bucket_name,
                "CUBITTS_ENV": cubitts_env,
            },
        )
        options.bucket.grant_write(shopify_inbound_fn)

        shopify_webhook_routes = [
            "/shopify/order/create",
            "/shopify/order/update",
            "/shopify/product/update",
            "/shopify/customer/create",
            "/shopify/customer/update",
        ]

        for route in shopify_webhook_routes:
            route_name = route_to_name(route)

            options.api.add_routes(
                path=route,
                methods=[aws_apigatewayv2.HttpMethod.POST],
                integration=aws_apigatewayv2_integrations.HttpLambdaIntegration(
                    f"Integration{route_name}",
                    shopify_inbound_fn,
                ),
            )
