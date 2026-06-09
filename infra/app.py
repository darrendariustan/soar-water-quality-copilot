import os
import aws_cdk as cdk
from stacks.s3_stack import S3Stack
from stacks.database_stack import DatabaseStack
from stacks.compute_stack import ComputeStack
from stacks.api_stack import ApiStack

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", "ap-southeast-1"),
)

tags = {
    "Project": "WaterForAll",
    "Component": "ComputerVision",
    "Environment": "dev",
    "Owner": "Member2",
}

s3_stack = S3Stack(app, "WaterForAllS3Stack", env=env, tags=tags)
db_stack = DatabaseStack(app, "WaterForAllDatabaseStack", env=env, tags=tags)
compute_stack = ComputeStack(
    app, "WaterForAllComputeStack",
    image_bucket=s3_stack.bucket,
    db_secret=db_stack.db_secret,
    env=env,
    tags=tags,
)
ApiStack(
    app, "WaterForAllApiStack",
    cv_function=compute_stack.cv_function,
    env=env,
    tags=tags,
)

app.synth()
