import boto3
import json
import os

def handler(event, context):

    print(event)
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    print(event['invocationSource'])
    
    print("event['sessionId']")
    print(event['sessionId'])
    print(slots)
    print(intent)
    validation_result = validate(slots=slots)
    if event['invocationSource'] == 'DialogCodeHook':
        if not validation_result['isValid']:
            response = {
                "sessionState": {
                    "dialogAction": {
                        'slotToElicit':validation_result['violatedSlot'],
                        "type": "ElicitSlot"
                    },
                    "intent": {
                        'name':intent,
                        'slots': slots
                        }
                }
            }
        else:
            print(slots['question']['value']['originalValue'])
            question = event['inputTranscript']
            res = invoke_model(question)
            print(res)
            response = {
                    "sessionState": {
                        "dialogAction": {
                            "type": "Close"
                        },
                        "intent": {
                            'name':intent,
                            'slots': slots,
                            'state': 'Fulfilled'
                            }
                    },
                    'messages': [
                        {
                            'contentType': 'PlainText',
                            'content': res['response']
                        }
                    ]
                }
            # save_item(id=event['sessionId'], input=res['question'], res=res['response'])

    if event['invocationSource'] == 'FulfillmentCodeHook':
        response = {
                "sessionState": {
                    "dialogAction": {
                        "type": "Delegate"
                    },
                    "intent": {
                        'name':intent,
                        'slots': slots
                    }
                }
            }
        
    return response
    
def invoke_model(input):
    # input = event.get('body')
    print("Question:", input)

    
    client = boto3.client('bedrock-agent-runtime')
    # client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
    knowledgeBaseId = os.getenv("KB_ID")
    modelArn = os.getenv("KB_MODEL_ARN")
    print(dir(client))
    print(modelArn)
    print(knowledgeBaseId)
    
    resp = client.retrieve_and_generate(
        input={
            'text': input
        },
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                'modelArn': modelArn,
                'knowledgeBaseId': knowledgeBaseId,
            },
            'type': 'KNOWLEDGE_BASE',
        }
    )
    
    
    
    kbTextResponse = resp['output']['text']
    print("KB response:", kbTextResponse)
    response = {
            "question": input,
            "response": kbTextResponse
    }
    
    return response
    
def save_item(input, res, id):
    table_name = os.getenv("TABLE_NAME")
    ddb = boto3.resource('dynamodb')
    table = ddb.Table(table_name)
    item = {
        "id": {'S': id},
        "question": {'S': input},
        "response": {'S': res}
    }
    table.put_item(
        Item=item,
        ReturnValues=None
    )
    response = {
        'statusCode': 200,
        'body': json.dumps({
            "question": input,
            "response": res,
        }),
    }
    return response


def validate(slots):
    if not slots['question']:
        return {
            'isValid': False,
            'violatedSlot': 'question'
        }

    return {
        'isValid': True
    }
