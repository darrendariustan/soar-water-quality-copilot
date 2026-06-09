import aws_cdk as cdk
from aws_cdk import (
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
    aws_lambda as lambda_,
)
from constructs import Construct


class ApiStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        cv_function: lambda_.IFunction,
        tags: dict,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        for k, v in tags.items():
            cdk.Tags.of(self).add(k, v)

        http_api = apigw.HttpApi(
            self, "CvHttpApi",
            api_name="waterforall-cv-api",
            cors_preflight=apigw.CorsPreflightOptions(
                allow_origins=["*"],
                allow_methods=[apigw.CorsHttpMethod.POST, apigw.CorsHttpMethod.GET],
                allow_headers=["Content-Type"],
            ),
        )

        lambda_integration = integrations.HttpLambdaIntegration(
            "CvIntegration", cv_function
        )

        http_api.add_routes(
            path="/cv/upload-url",
            methods=[apigw.HttpMethod.POST],
            integration=lambda_integration,
        )
        http_api.add_routes(
            path="/cv/process",
            methods=[apigw.HttpMethod.POST],
            integration=lambda_integration,
        )
        http_api.add_routes(
            path="/cv/results/{result_id}",
            methods=[apigw.HttpMethod.GET],
            integration=lambda_integration,
        )

        cdk.CfnOutput(self, "ApiEndpoint", value=http_api.api_endpoint)
