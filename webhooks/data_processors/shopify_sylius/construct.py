from aws_cdk import (
    Duration,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_event_sources,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3 as s3,
    aws_sqs as sqs,
)
from constructs import Construct


class ShopifyToSyliusProcessor(Construct):
    def __init__(self, scope: Construct, id: str, bucket: s3.Bucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        rule = events.Rule(
            self,
            "ShopifyOrderCreateRule",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={
                    "bucket": {"name": [bucket.bucket_name]},
                    "object": {"key": [{"prefix": "shopify/orders/create"}]},
                },
            ),
        )

        queue = sqs.Queue(
            self,
            "ShopifyToSyliusQueue",
            visibility_timeout=Duration.seconds(300),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=sqs.Queue(
                    self,
                    "ShopifyToSyliusDLQ",
                    visibility_timeout=Duration.seconds(300),
                ),
            ),
        )
        rule.add_target(targets.SqsQueue(queue))

        lambda_fn = _lambda.Function(
            self,
            "ShopifyToSyliusLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="send_to_sylius.handler",
            timeout=Duration.seconds(60),
            code=_lambda.Code.from_asset(
                "webhooks/data_processors/shopify_sylius/lambdas"
            ),
        )
        bucket.grant_read(lambda_fn)
        queue.grant_consume_messages(lambda_fn)
        lambda_fn.add_event_source(lambda_event_sources.SqsEventSource(queue))