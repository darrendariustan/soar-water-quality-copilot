import aws_cdk as cdk
from aws_cdk import aws_s3 as s3
from constructs import Construct


class S3Stack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, tags: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        for k, v in tags.items():
            cdk.Tags.of(self).add(k, v)

        self.bucket = s3.Bucket(
            self, "CvImagesBucket",
            bucket_name="waterforall-dev-cv-images",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="ExpireRawAfter30Days",
                    prefix="raw/",
                    expiration=cdk.Duration.days(30),
                    enabled=True,
                )
            ],
        )

        cdk.CfnOutput(self, "BucketName", value=self.bucket.bucket_name)
