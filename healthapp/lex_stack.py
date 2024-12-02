from aws_cdk import (
    Duration,
    Stack,
    aws_lex as lex,
    aws_lambda as _lambda,
    aws_iam as iam,
)
from constructs import Construct
# from os.path import join

class LexStack(Stack):
    def __init__(self, scope: Construct, id: str, lex_lambda_hook, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Lambda function for intent fulfillment
        # pizza_order_lambda = _lambda.Function(
        #     self,
        #     "PizzaOrderHandler",
        #     runtime=_lambda.Runtime.PYTHON_3_9,
        #     handler="pizza_order.handler",
        #     code=_lambda.Code.from_asset(join("lambda")),
        #     timeout=Duration.seconds(15),
        #     environment={},
        # )
        
        # Permissions for Lambda to log
        lex_lambda_hook.add_to_role_policy(
            iam.PolicyStatement(
                actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                resources=["*"],
            )
        )

        # Lex bot
        order_pizza_intent = lex.CfnIntent(
            self,
            "OrderPizzaIntent",
            name="OrderPizza",
            sample_utterances=[
                {"utterance": "I want to ask a question"},
                {"utterance": "Ask a {question}"},
            ],
            fulfillment_code_hook=lex.CfnIntent.FulfillmentCodeHookProperty(
                lambda_code_hook=lex.CfnIntent.LambdaCodeHookProperty(
                    lambda_arn=lex_lambda_hook.function_arn
                )
            ),
            slots=[
                lex.CfnSlotProperty(
                    name="question",
                    slot_type_name="AMAZON.AlphaNumeric",
                    slot_constraint="Required",
                    value_elicitation_setting=lex.CfnSlotValueElicitationSettingProperty(
                        slot_constraint="Required",
                        prompt=lex.CfnPromptProperty(
                            max_retries=3,
                            messages=[
                                {"content": "What are you suffering from?", "content_type": "PlainText"}
                            ],
                        ),
                    ),
                )
            ],
        )

        lex_bot = lex.CfnBot(
            self,
            "PizzaOrderBot",
            name="PizzaOrderBot",
            role_arn=lex_lambda_hook.role.role_arn,
            intents=[{"intent_name": order_pizza_intent.name}],
            idle_session_ttl_in_seconds=300,
            bot_locale=[
                {
                    "locale_id": "en_US",
                    "nlu_intent_confidence_threshold": 0.4,
                    "voice_settings": {"voice_id": "Joanna"},
                }
            ],
            data_privacy={"child_directed": False},
        )