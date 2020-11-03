#!/usr/bin/env python
import base64
import json
import os
from hashlib import sha256
from typing import Dict, List

from constructs import Construct
from cdktf import (  # type: ignore
    App,
    S3Backend,
    TerraformOutput,
    TerraformResourceLifecycle,
    TerraformStack,
)

from build import package_assets  # type: ignore
from imports.aws import (  # type: ignore
    AwsProvider,
    ApiGatewayDeployment,
    ApiGatewayIntegration,
    ApiGatewayMethod,
    ApiGatewayResource,
    ApiGatewayRestApi,
    CloudwatchLogGroup,
    DataAwsCallerIdentity,
    DataAwsS3Bucket,
    DynamodbTable,
    DynamodbTableAttribute,
    IamPolicy,
    IamPolicyAttachment,
    IamRole,
    LambdaFunction,
    LambdaFunctionEnvironment,
    LambdaFunctionTracingConfig,
    LambdaLayerVersion,
    LambdaPermission,
    S3BucketObject,
)


class SMSBridgeStack(TerraformStack):
    def create_dynamodb_table(self) -> None:
        self.dynamodb_table = DynamodbTable(
            self, 'sms_bridge_state_dynamodb_table',
            lifecycle=TerraformResourceLifecycle(
                prevent_destroy=True,
            ),
            name='sms-bridge-state',
            hash_key='user_number',
            attribute=[
                DynamodbTableAttribute(name='user_number', type='S')
            ],
            billing_mode='PAY_PER_REQUEST',
        )

    def create_dependency_layer(self, package_file: str) -> None:
        dependency_package = S3BucketObject(
            self, 'dependency_deployment_package',
            bucket=self.lambda_bucket.bucket,
            key=f'sms_bridge/{os.path.basename(package_file)}',
            source=package_file,
        )
        with open(package_file, 'rb') as f:
            hash_bytes = sha256(f.read()).digest()
            source_hash = base64.b64encode(hash_bytes).decode('UTF-8')

        self.dependency_layer = LambdaLayerVersion(
            self, 'dependency_layer',
            layer_name='SMSBridgeDependencyLayer',
            s3_bucket=dependency_package.bucket,
            s3_key=dependency_package.key,
            compatible_runtimes=['python3.8'],
            source_code_hash=source_hash,
        )

    def create_lambda_role(self) -> IamRole:
        role = IamRole(
            self, 'lambda_execution_role',
            name='sms_bridge_lambda_execution_role',
            assume_role_policy=json.dumps({
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Effect': 'allow',
                        'Action': ['sts:AssumeRole'],
                        'Principal': {
                            'Service': 'lambda.amazonaws.com',
                        },
                    },
                ],
            }),
        )
        policy = IamPolicy(
            self, 'lambda_cloudwatch_log_policy',
            name='sms_bridge_lambda_cloudwatch_log_policy',
            policy=json.dumps({
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Effect': 'Allow',
                        'Action': [
                            'logs:CreateLogStream',
                            'logs:PutLogEvents',
                            'xray:PutTelemetryRecords',
                            'xray:PutTraceSegments',
                        ],
                        'Resource': '*',
                    },
                    {
                        'Effect': 'Allow',
                        'Action': [
                            'dynamodb:PutItem',
                            'dynamodb:Scan',
                        ],
                        'Resource': self.dynamodb_table.arn,
                    },
                    {
                        'Effect': 'Allow',
                        'Action': [
                            's3:GetObject',
                        ],
                        'Resource': f'{self.config_bucket.arn}/*',
                    },
                ],
            }),
        )
        IamPolicyAttachment(
            self, 'lambda_role_policy_attachment',
            name='lambda_role_policy_attachment',
            policy_arn=policy.arn,
            roles=[role.name],
        )

        return role

    def create_lambda_function(self, path: str) -> LambdaFunction:
        function_name: str = f'{path.title()}Receiver'
        CloudwatchLogGroup(
            self, f'{path}_receive_log_group',
            name=f'/aws/lambda/{function_name}',
            retention_in_days=14,
        )
        return LambdaFunction(
            self, f'{path}_receive_function',
            function_name=function_name,
            handler=f'aws_lambda.receive_{path}.handler',
            runtime='python3.8',
            role=self.lambda_execution_role.arn,
            environment=[self.lambda_environment],
            layers=[self.dependency_layer.arn],
            memory_size=128,
            timeout=30,
            tracing_config=[self.lambda_tracing_config],
            s3_bucket=self.function_package.bucket,
            s3_key=self.function_package.key,
            source_code_hash=self.function_source_hash,
        )

    def create_lambda_setup(self) -> None:
        layer_package_file, function_package_file = package_assets()
        self.create_dependency_layer(layer_package_file)
        self.lambda_environment: LambdaFunctionEnvironment = \
            LambdaFunctionEnvironment(variables={
                'bridge_env': 'PROD',
                'bridge_config':
                    f's3://{self.config_bucket.bucket}/bridge.json',
                'state_dynamodb_table': self.dynamodb_table.name,
            })
        self.lambda_tracing_config: LambdaFunctionTracingConfig = \
            LambdaFunctionTracingConfig(mode='Active')
        self.function_package: S3BucketObject = S3BucketObject(
            self, 'function_deployment_package',
            bucket=self.lambda_bucket.bucket,
            key=f'sms_bridge/{os.path.basename(function_package_file)}',
            source=function_package_file,
        )
        self.lambda_execution_role: IamRole = self.create_lambda_role()
        with open(function_package_file, 'rb') as f:
            hash_bytes = sha256(f.read()).digest()
            self.function_source_hash: str = base64.b64encode(
                hash_bytes).decode('UTF-8')

        self.functions: Dict[str, LambdaFunction] = {
            path: self.create_lambda_function(path)
            for path in ('telegram', 'twilio')
        }

    def create_api_gateway(self) -> None:
        api = ApiGatewayRestApi(
            self, 'sms_bridge_rest_api',
            name='SMSBridgeApi',
        )

        integrations: List[ApiGatewayIntegration] = []
        for path, function in self.functions.items():
            resource = ApiGatewayResource(
                self, f'sms_bridge_{path}_api_resource',
                path_part=path,
                rest_api_id=api.id,
                parent_id=api.root_resource_id,
            )
            method = ApiGatewayMethod(
                self, f'sms_bridge_{path}_api_method',
                rest_api_id=api.id,
                resource_id=resource.id,
                http_method='POST',
                authorization='NONE',
            )
            integrations.append(ApiGatewayIntegration(
                self, f'sms_bridge_{path}_api_integration',
                rest_api_id=api.id,
                resource_id=resource.id,
                http_method=method.http_method,
                integration_http_method='POST',
                type='AWS_PROXY',
                uri=function.invoke_arn,
            ))
            LambdaPermission(
                self, f'sms_bridge_{path}_lambda_permission',
                depends_on=[function],
                statement_id='AllowExecutionFromAPIGateway',
                action='lambda:InvokeFunction',
                function_name=function.function_name,
                principal='apigateway.amazonaws.com',
                source_arn=(
                    f'arn:aws:execute-api:{self.region}:{self.account_id}:'
                    f'{api.id}/*/{method.http_method}{resource.path}'
                ),
            )

        ApiGatewayDeployment(
            self, 'sms_bridge_api_deployment',
            depends_on=integrations,
            rest_api_id=api.id,
            stage_name=self.stage,
        )

    def create_outputs(self) -> None:
        TerraformOutput(self, 'api_gateway_url', value='arst')

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)
        self.region: str = 'us-east-1'
        self.stage: str = 'dev'

        AwsProvider(self, 'aws', region=self.region)
        S3Backend(
            self,
            bucket='smartcat-tfstate',
            key='sms-bridge.tfstate',
            region=self.region,
        )
        caller_id = DataAwsCallerIdentity(self, 'caller_id')
        self.account_id = caller_id.account_id
        self.config_bucket = DataAwsS3Bucket(
            self, 'config_bucket',
            bucket='smartcat-sms-bridge-config',
        )
        self.lambda_bucket = DataAwsS3Bucket(
            self, 'lambda_bucket',
            bucket='smartcat-lambda-deployment-bucket',
        )

        self.create_dynamodb_table()
        self.create_lambda_setup()
        self.create_api_gateway()
        self.create_outputs()


app = App()
SMSBridgeStack(app, 'tfcdk')
app.synth()
