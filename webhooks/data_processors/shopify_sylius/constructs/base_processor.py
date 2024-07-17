from dataclasses import dataclass

from aws_cdk import (
    Duration,
    aws_events,
    aws_events_targets,
    aws_lambda,
    aws_lambda_event_sources,
    aws_s3,
    aws_sqs,
)
from constructs import Construct

from webhooks.utils import route_to_name


@dataclass
class ShopifyToSyliusProcessorOptions:
    bucket: aws_s3.Bucket
    prefix: str
    handler: str
    concurrency: int = 50


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

        name = route_to_name(options.prefix)
        clean_prefix = options.prefix.strip("/")

        rule = aws_events.Rule(
            self,
            f"{name}Rule",
            event_pattern=aws_events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={
                    "bucket": {"name": [options.bucket.bucket_name]},
                    "object": {"key": [{"prefix": clean_prefix}]},
                },
            ),
        )

        queue = aws_sqs.Queue(
            self,
            f"{name}Queue",
            visibility_timeout=Duration.seconds(300),
            dead_letter_queue=aws_sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=aws_sqs.Queue(
                    self,
                    f"{name}DLQ",
                    visibility_timeout=Duration.seconds(300),
                    retention_period=Duration.days(14),
                ),
            ),
        )
        rule.add_target(aws_events_targets.SqsQueue(queue))

        lambda_fn = aws_lambda.Function(
            self,
            f"{name}Lambda",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            handler=options.handler,
            timeout=Duration.seconds(120),
            reserved_concurrent_executions=options.concurrency,
            code=aws_lambda.Code.from_asset(
                "webhooks/data_processors/shopify_sylius/lambdas"
            ),
            environment={
                "CUBITTS_ENV": cubitts_env,
                "PREFIX": clean_prefix,
            },
        )
        options.bucket.grant_read(lambda_fn)
        queue.grant_consume_messages(lambda_fn)
        lambda_fn.add_event_source(
            aws_lambda_event_sources.SqsEventSource(queue, batch_size=1),
        )
