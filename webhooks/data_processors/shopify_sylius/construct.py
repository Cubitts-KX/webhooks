from dataclasses import dataclass

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


@dataclass
class ShopifyToSyliusProcessorOptions:
    bucket: s3.Bucket
    prefix: str
    handler: str
    concurrency: int = 10


class ShopifyToSyliusProcessor(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        options: ShopifyToSyliusProcessorOptions,
        cubitts_env: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        name = construct_name(options.prefix)

        rule = events.Rule(
            self,
            f"{name}Rule",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={
                    "bucket": {"name": [options.bucket.bucket_name]},
                    "object": {"key": [{"prefix": options.prefix}]},
                },
            ),
        )

        queue = sqs.Queue(
            self,
            f"{name}Queue",
            visibility_timeout=Duration.seconds(300),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=sqs.Queue(
                    self,
                    f"{name}DLQ",
                    visibility_timeout=Duration.seconds(300),
                ),
            ),
        )
        rule.add_target(targets.SqsQueue(queue))

        lambda_fn = _lambda.Function(
            self,
            f"{name}Lambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler=options.handler,
            timeout=Duration.seconds(60),
            code=_lambda.Code.from_asset(
                "webhooks/data_processors/shopify_sylius/lambdas"
            ),
            environment={
                "CUBITTS_ENV": cubitts_env,
                "PREFIX": options.prefix,
            },
        )
        options.bucket.grant_read(lambda_fn)
        queue.grant_consume_messages(lambda_fn)
        lambda_fn.add_event_source(
            lambda_event_sources.SqsEventSource(queue),
        )


def construct_name(prefix):
    service, resource, action = prefix.split("/")
    return f"{service.capitalize()}ToSylius{resource.capitalize()}{action.capitalize()}"
