#!/usr/bin/env python3

import aws_cdk as cdk

from webhooks.webhooks_stack import WebhooksStack

app = cdk.App()
WebhooksStack(
    app,
    "WebhooksStack",
    cubitts_env="staging",
)

app.synth()
