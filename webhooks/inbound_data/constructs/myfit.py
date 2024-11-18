# See here for the webhooks available and the bodies they send:
# https://doc.myfit-solutions.com/apidocumentation/webhook.html

from dataclasses import dataclass

from aws_cdk import aws_apigatewayv2, aws_apigatewayv2_integrations, aws_lambda, aws_s3
from constructs import Construct

from webhooks.utils import route_to_name


@dataclass
class MyFitInboundOptions:
    bucket: aws_s3.Bucket
    api: aws_apigatewayv2.HttpApi


class MyFitInbound(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        options: MyFitInboundOptions,
        cubitts_env: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        myfit_inbound_fn = aws_lambda.Function(
            self,
            "Function",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            handler="myfit.store_body",
            code=aws_lambda.Code.from_asset("webhooks/inbound_data/lambdas"),
            environment={
                "BUCKET_NAME": options.bucket.bucket_name,
                "CUBITTS_ENV": cubitts_env,
            },
        )
        options.bucket.grant_write(myfit_inbound_fn)

        webhook_routes = [
            "/myfit/scan/finished",
            # TODO - add error captures and potentially in progress.
        ]

        for route in webhook_routes:
            route_name = route_to_name(route)

            options.api.add_routes(
                path=route,
                methods=[aws_apigatewayv2.HttpMethod.POST],
                integration=aws_apigatewayv2_integrations.HttpLambdaIntegration(
                    f"Integration{route_name}",
                    myfit_inbound_fn,
                ),
            )
