from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as _apigateway,
    aws_ec2 as ec2,    
    aws_iam as iam,
    aws_ssm as ssm,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr as ecr,
    aws_dynamodb as _dynamodb,
    Duration as Duration
)
from constructs import Construct

class HealthappStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = _dynamodb.Table(self, "dynamodbTable",
                                table_name="health_app_ai",
                                partition_key=_dynamodb.Attribute(name="id", type=_dynamodb.AttributeType.STRING))
        
        # Defines role for the AWS Lambda functions
        # role = iam.Role(self, "Gen-AI-Lambda-Policy", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        # role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        # role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"))
        # role.attach_inline_policy(iam.Policy(self, "br-invoke-policy",
        #     statements=[iam.PolicyStatement(
        #         effect=iam.Effect.ALLOW,
        #         actions=[
        #             "bedrock:ListFoundationModels",
        #             "bedrock:GetFoundationModel",
        #             "bedrock:InvokeModel"
        #             ],
        #         resources=["*"]
        #     )]
        # ))

        # Define IAM Role for Lambda
        lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )


        # Define custom Bedrock policy
        bedrock_policy = iam.PolicyStatement(
            actions=[
                "bedrock:InvokeModel",  # Allow invoking Bedrock models
                # "bedrock:ListModels",  # Allow listing available Bedrock models
                "bedrock:InvokeModelWithResponseStream"  # For streaming responses (if needed)
            ],
            resources=["*"]  # You can restrict to specific models if needed
        )

        # Attach Bedrock Invoke Policy to the Role
        lambda_role.add_to_policy(bedrock_policy)
        # lambda_role.add_managed_policy(
        #     iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockInvokeFullAccess")
        # )

        # Add Basic Execution Role for Lambda logging to CloudWatch
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )


        invoke_model_lambda = _lambda.Function(self, "invoke_model_lambda",
                                                      runtime=_lambda.Runtime.PYTHON_3_10,
                                                      handler='invoke_model_lambda.lambda_handler',
                                                      code=_lambda.Code.from_asset('src'),
                                                      role=lambda_role,
                                                      timeout=Duration.minutes(15)
                                                    )
        get_chats = _lambda.Function(self, "get_chats_function",
                                                      runtime=_lambda.Runtime.PYTHON_3_10,
                                                      handler='get_chats.lambda_handler',
                                                      code=_lambda.Code.from_asset('src'),
                                                      role=lambda_role
                                                    )
        health_api = _apigateway.RestApi(
            self,
            'health_rest_api'
        )

        get_chats.add_environment(key="TABLE_NAME", value=table.table_name)
        table.grant_write_data(get_chats)

        health_api.root.add_resource("health").add_method(
            "GET",
            _apigateway.LambdaIntegration(
                handler=get_chats
            )
        )