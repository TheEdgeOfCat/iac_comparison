from aws_cdk import core

from cdk import SMSTelegramBridgeStack


app = core.App()
SMSTelegramBridgeStack(
    app, 'SMSBridge',
    env={'region': 'us-east-1'},
)

app.synth()
