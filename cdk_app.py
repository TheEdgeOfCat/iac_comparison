import os

from aws_cdk import core

from cdk import SMSTelegramBridgeStack


app = core.App()
stage = os.getenv('STAGE', 'dev')
SMSTelegramBridgeStack(
    app, f'SMSBridge{stage.title()}',
    stage=stage,
    env={'region': 'us-east-1'},
)

app.synth()
