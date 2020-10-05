from aws_cdk import aws_apigateway, aws_dynamodb, aws_s3, core

from cdk.lambda_functions import SMSTelegramBridgeLambdaFunctionConstruct


class SMSTelegramBridgeStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        state_table = aws_dynamodb.Table(
            self, 'SMSTelegramBridgeStateTable',
            table_name='sms-bridge',
            partition_key=aws_dynamodb.Attribute(
                name='user_number',
                type=aws_dynamodb.AttributeType.STRING,
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        config_bucket = aws_s3.Bucket.from_bucket_name(
            self, 'ConfigBucket',
            'edifice-config',
        )

        lambda_functions = SMSTelegramBridgeLambdaFunctionConstruct(
            self,
            'SMSTelegramBridgeLambdaFunctionConstruct',
            config_bucket.name,
            state_table.table_name,
        )

        api = aws_apigateway.RestApi(
            self, 'SMSTelegramBridgeApi',
            rest_api_name='SMSTelegramBridgeApi',
        )
        telegram_resource = api.root.add_resource('telegram')
        telegram_resource.add_method('POST', aws_apigateway.LambdaIntegration(
            handler=lambda_functions.telegram_receive_function,
        ))
        twilio_resource = api.root.add_resource('twilio')
        twilio_resource.add_method('POST', aws_apigateway.LambdaIntegration(
            handler=lambda_functions.twilio_receive_function,
        ))

        config_bucket.grant_read(lambda_functions.telegram_receive_function)
        config_bucket.grant_read(lambda_functions.twilio_receive_function)
        state_table.grant_write_data(
            lambda_functions.telegram_receive_function,
        )
        state_table.grant_read_data(
            lambda_functions.twilio_receive_function,
        )
