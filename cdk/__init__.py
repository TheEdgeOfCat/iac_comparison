from aws_cdk import aws_apigateway, aws_dynamodb, aws_lambda, aws_s3, core

from cdk.lambda_function import SMSTelegramBridgeLambdaFunction


class SMSTelegramBridgeStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        stage: str,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.stage = stage
        self.create_dynamodb_table()
        self.create_lambda_dependency_layer()
        self.config_bucket = aws_s3.Bucket.from_bucket_name(
            self, 'ConfigBucket',
            'smartcat-sms-bridge-config',
        )

        api = aws_apigateway.RestApi(
            self, 'SMSTelegramBridgeApi',
            rest_api_name=self.get_full_name('SMSTelegramBridgeApi'),
        )
        SMSTelegramBridgeLambdaFunction(
            self, 'TelegramLambdaFunction',
            function_name=self.get_full_name('TelegramReceiverLambdaFunction'),
            handler='aws_lambda.receive_telegram.handler',
            config_bucket=self.config_bucket,
            state_table=self.state_table,
            dependency_layer=self.dependency_layer,
            api=api,
            endpoint='telegram',
        )
        SMSTelegramBridgeLambdaFunction(
            self, 'TwilioReceiverLambdaFunction',
            function_name=self.get_full_name('TwilioReceiverLambdaFunction'),
            handler='aws_lambda.receive_twilio.handler',
            config_bucket=self.config_bucket,
            state_table=self.state_table,
            dependency_layer=self.dependency_layer,
            api=api,
            endpoint='twilio',
        )

    def get_full_name(self, name) -> str:
        return f'{name}-{self.stage}'

    def create_lambda_dependency_layer(self) -> None:
        dependency_asset = aws_lambda.Code.from_asset(
            path='./',
            bundling=core.BundlingOptions(
                image=core.BundlingDockerImage.from_asset('./')
            )
        )
        self.dependency_layer = aws_lambda.LayerVersion(
            self, 'DependencyLayer',
            code=dependency_asset,
            compatible_runtimes=[
                aws_lambda.Runtime.PYTHON_3_6,
                aws_lambda.Runtime.PYTHON_3_7,
                aws_lambda.Runtime.PYTHON_3_8,
            ],
            description='A layer containing all Python dependencies',
        )

    def create_dynamodb_table(self) -> None:
        self.state_table = aws_dynamodb.Table(
            self, 'SMSTelegramBridgeStateTable',
            table_name=self.get_full_name('sms-bridge'),
            partition_key=aws_dynamodb.Attribute(
                name='user_number',
                type=aws_dynamodb.AttributeType.STRING,
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
        )
