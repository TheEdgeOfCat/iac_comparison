import os
from typing import List

from aws_cdk import aws_apigateway, aws_dynamodb, aws_lambda, aws_s3, core


def get_lambda_exclude_list() -> List[str]:
    files = set(os.listdir()) - set((
        'aws_lambda',
        'bridge',
    ))

    return list(files)


code_asset = aws_lambda.Code.from_asset(
    path='./',
    exclude=get_lambda_exclude_list(),
)


class SMSTelegramBridgeLambdaFunction(core.Construct):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        function_name: str,
        handler: str,
        config_bucket: aws_s3.Bucket,
        state_table: aws_dynamodb.Table,
        dependency_layer: aws_lambda.LayerVersion,
        api: aws_apigateway.RestApi,
        endpoint: str,
    ) -> None:
        super().__init__(scope, id)
        environment = {
            'bridge_env': 'PROD',
            'bridge_config': f's3://{config_bucket.bucket_name}/bridge.json',
            'state_dynamodb_table': state_table.table_name,
        }
        self.function = aws_lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            layers=[dependency_layer],
            code=code_asset,
            handler=handler,
            timeout=core.Duration.seconds(30),
            retry_attempts=0,
            environment=environment,
        )
        function_resource = api.root.add_resource(endpoint)
        function_resource.add_method('POST', aws_apigateway.LambdaIntegration(
            handler=self.function,
        ))
        config_bucket.grant_read(self.function)
        state_table.grant_write_data(self.function)
