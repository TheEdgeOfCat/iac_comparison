import os
from typing import List

from aws_cdk import aws_lambda, core


class SMSTelegramBridgeLambdaFunctionConstruct(core.Construct):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        config_bucket_name: str,
        dynamodb_table_name: str,
    ) -> None:
        super().__init__(scope, id)
        environment = {
            'edifice_bridge_env': 'PROD',
            'edifice_bridge_config': f's3://{config_bucket_name}/bridge.json',
            'state_dynamodb_table': dynamodb_table_name,
        }
        dependency_asset = aws_lambda.Code.from_asset(
            path='./',
            bundling=core.BundlingOptions(
                image=core.BundlingDockerImage.from_asset('./')
            )
        )
        dependency_layer = aws_lambda.LayerVersion(
            self, 'DependencyLayer',
            code=dependency_asset,
            compatible_runtimes=[
                aws_lambda.Runtime.PYTHON_3_6,
                aws_lambda.Runtime.PYTHON_3_7,
                aws_lambda.Runtime.PYTHON_3_8,
            ],
            description='A layer containing all Python dependencies',
        )
        code_asset = aws_lambda.Code.from_asset(
            path='./',
            exclude=self._get_lambda_exclude_list(),
        )
        self.telegram_receive_function = aws_lambda.Function(
            self, 'TelegramReceiveFunction',
            function_name='TelegramReceiveFunction',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            layers=[dependency_layer],
            code=code_asset,
            handler='aws_lambda.receive_telegram.handler',
            timeout=core.Duration.seconds(30),
            retry_attempts=0,
            environment=environment,
        )
        self.twilio_receive_function = aws_lambda.Function(
            self, 'TwilioReceiveFunction',
            function_name='TwilioReceiveFunction',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            layers=[dependency_layer],
            code=code_asset,
            handler='aws_lambda.receive_twilio.handler',
            timeout=core.Duration.seconds(30),
            retry_attempts=0,
            environment=environment,
        )

    def _get_lambda_exclude_list(self) -> List[str]:
        files = set(os.listdir()) - set((
            'aws_lambda',
            'edifice_bridge',
        ))

        return list(files)
