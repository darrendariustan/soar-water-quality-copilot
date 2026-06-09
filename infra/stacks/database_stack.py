import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2, aws_rds as rds, aws_secretsmanager as secretsmanager
from constructs import Construct


class DatabaseStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, tags: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        for k, v in tags.items():
            cdk.Tags.of(self).add(k, v)

        vpc = ec2.Vpc(
            self, "CvVpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(name="private", subnet_type=ec2.SubnetType.PRIVATE_ISOLATED, cidr_mask=24)
            ],
        )

        self.db_secret = rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_16)

        db_sg = ec2.SecurityGroup(self, "DbSg", vpc=vpc, description="CV database security group")

        self.db_instance = rds.DatabaseInstance(
            self, "CvDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_16),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            security_groups=[db_sg],
            database_name="waterforall_cv",
            credentials=rds.Credentials.from_generated_secret("cvadmin"),
            deletion_protection=False,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            backup_retention=cdk.Duration.days(0),
            multi_az=False,
        )

        self.db_secret = self.db_instance.secret

        cdk.CfnOutput(self, "DbEndpoint", value=self.db_instance.db_instance_endpoint_address)
        cdk.CfnOutput(self, "DbSecretArn", value=self.db_instance.secret.secret_arn)
