import aws_cdk as cdk
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct

from webhooks.webhooks_stack import WebhooksStack


class Production(cdk.Stage):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        WebhooksStack(
            self,
            "Webhooks",
            cubitts_env="production",
            env=cdk.Environment(
                account="658056508030",
                region="eu-west-1",
            ),
        )


class Staging(cdk.Stage):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        WebhooksStack(
            self,
            "Webhooks",
            cubitts_env="staging",
            env=cdk.Environment(
                account="658056508030",
                region="eu-west-1",
            ),
        )


class PipelineStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repo = "Cubitts-KX/webhooks"
        branch = "main"  # Yeah, both prod and staging stacks are deployed against main branch
        # This is so we have staging and prod webhooks active and our deployed services are working
        # for both environments.
        # If you want to deploy a development stack, see the README for instructions.

        pipeline = CodePipeline(
            self,
            "DeploymentPipeline",
            pipeline_name="webhooks",
            synth=ShellStep(
                "Synth",
                input=CodePipelineSource.connection(
                    repo,
                    branch,
                    connection_arn="arn:aws:codestar-connections:eu-west-1:658056508030:connection/3a8aca7a-ed7c-414b-9e21-3a7b22e4935d",
                ),
                commands=[
                    "npm install -g aws-cdk",
                    "python -m pip install -r requirements.txt",
                    "cdk synth",
                ],
            ),
        )

        pipeline.add_stage(Production(self, "Production"))
        pipeline.add_stage(Staging(self, "Staging"))
