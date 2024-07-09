#!/usr/bin/env python3
import aws_cdk as cdk

from cdk_pipeline import PipelineStack

app = cdk.App()
PipelineStack(
    app,
    "WebhooksPipeline",
    env=cdk.Environment(
        account="658056508030",
        region="eu-west-1",
    ),
)

app.synth()
