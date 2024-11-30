import json
import os
import random

import boto3

table_name = os.environ.get("TABLE_NAME")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    print(f"Received event: {event}")
    print(f"table_name: {table_name}")
    weather_event = json.loads(event['body'])
    weather_id = str(random.randrange(100, 999))
    weather_name = weather_event['weather']
    weather_town = weather_event['town']

    print(f"weather_town: {weather_town}")
    print(f"weather_name: {weather_name}")
    item = {
        "id": weather_id,
        "weather": weather_name,
        "town": weather_town
    }
    try:
        table.put_item(
            Item=item,
            ReturnValues='NONE',
        )
        return {
            "statusCode": 200,
            "body": json.dumps({
                'statusCode': 200,
                'message': 'Weather successfully created!'
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "statusCode": 500,
                "message": f"An error occured while creating the weather!{e}"
            })
        }