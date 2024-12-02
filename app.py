#!/usr/bin/env python3
import os

import aws_cdk as cdk

from healthapp.healthapp_stack import HealthappStack
from healthapp.lex_stack import LexStack


app = cdk.App()
mainstack = HealthappStack(app, "HealthappStack",
    # env=cdk.Environment(account='059609450404', region='us-east-1'),
    )
# LexStack(app, "lexStack",lex_lambda_hook= mainstack.kbQueryLambdaFunction)

app.synth()
