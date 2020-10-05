# Edifice Twilio-Telegram bridge

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Poetry

This project uses poetry as its dependency management tool. To start, run:

`poetry install`

This will install all dependencies, including dev tools and cdk libraries into
a virtualenvironment in the `.venv` directory.

Running commands in the virtualenv can be achieved by spawning a shell:

`poetry shell`

Or running the command directly:

`poetry run <command>`

## CDK commands

CDK commands are run through

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
