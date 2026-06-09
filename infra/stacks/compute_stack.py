import aws_cdk as cdk
from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct


class ComputeStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        image_bucket: s3.IBucket,
        db_secret,
        tags: dict,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        for k, v in tags.items():
            cdk.Tags.of(self).add(k, v)

        execution_role = iam.Role(
            self, "CvLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
            ],
        )

        # Least-privilege policies
        execution_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:GetObject", "s3:PutObject"],
            resources=[image_bucket.arn_for_objects("*")],
        ))
        execution_role.add_to_policy(iam.PolicyStatement(
            actions=["secretsmanager:GetSecretValue"],
            resources=[db_secret.secret_arn],
        ))
        execution_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "rekognition:DetectImageProperties",
                "rekognition:DetectLabels",
            ],
            resources=["*"],
        ))

        # Container image Lambda built from backend/
        self.cv_function = lambda_.DockerImageFunction(
            self, "CvFunction",
            code=lambda_.DockerImageCode.from_image_asset(
                "../backend",
                file="Dockerfile",
                cmd=["src.lambda_handler.handler"],
            ),
            memory_size=1024,
            timeout=cdk.Duration.seconds(30),
            role=execution_role,
            environment={
                "CV_PROVIDER": "local",
                "DB_SECRET_ARN": db_secret.secret_arn,
            },
        )

        # Trigger on raw/ prefix S3 events
        image_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(self.cv_function),
            s3.NotificationKeyFilter(prefix="raw/"),
        )

        cdk.CfnOutput(self, "FunctionArn", value=self.cv_function.function_arn)
