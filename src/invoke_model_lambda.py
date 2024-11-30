import boto3
import json

def lambda_handler(event, context):
    print(event)

    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'
    )
    
    print(event)
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    print(event['invocationSource'])
    print(slots)
    print(intent)
    
    input = {
        "modelId": "anthropic.claude-v2",
        "contentType": "application/json",
        "accept": "*/*",
        "body": "{\n  \"prompt\": \"\\n\\nHuman: story of two dogs\\n\\nAssistant:\",\n  \"max_tokens_to_sample\": 300\n}"
    }

    response = bedrock.invoke_model(
        body=input["body"],
        modelId=input["modelId"],
        accept=input["accept"],
        contentType=input["contentType"]
    )

    response_body = json.loads(response['body'].read())
    print("Model Response")
    print(response_body['completion'])
    response = {
                "sessionState": {
                    "dialogAction": {
                        'slotToElicit':'help',
                        "type": "ElicitSlot"
                    },
                    "intent": {
                        'name':intent,
                        'slots': slots
                        
                        }
                }
    }
    return response

    


# def lambda_handler(event, context):
    
#     print(event)
#     slots = event['sessionState']['intent']['slots']
#     intent = event['sessionState']['intent']['name']
#     print(event['invocationSource'])
#     print(slots)
#     print(intent)
    
#     response = {
#                 "sessionState": {
#                     "dialogAction": {
#                         'slotToElicit':'help',
#                         "type": "ElicitSlot"
#                     },
#                     "intent": {
#                         'name':intent,
#                         'slots': slots
                        
#                         }
#                 }
#     }
#     return response
    
#     # validation_result = validate(event['sessionState']['intent']['slots'])
    
#     # if event['invocationSource'] == 'DialogCodeHook':
#     #     if not validation_result['isValid']:
            
#     #         if 'message' in validation_result:
            
#                 # response = {
#                 # "sessionState": {
#                 #     "dialogAction": {
#                 #         'slotToElicit':validation_result['violatedSlot'],
#                 #         "type": "ElicitSlot"
#                 #     },
#                 #     "intent": {
#                 #         'name':intent,
#                 #         'slots': slots
                        
#                 #         }
#                 # },
#     #             "messages": [
#     #                 {
#     #                     "contentType": "PlainText",
#     #                     "content": validation_result['message']
#     #                 }
#     #             ]
#     #           } 
#     #         else:
#     #             response = {
#     #             "sessionState": {
#     #                 "dialogAction": {
#     #                     'slotToElicit':validation_result['violatedSlot'],
#     #                     "type": "ElicitSlot"
#     #                 },
#     #                 "intent": {
#     #                     'name':intent,
#     #                     'slots': slots
                        
#     #                     }
#     #             }
#     #           } 
    
#     #         return response
           
#     #     else:
#     #         response = {
#     #         "sessionState": {
#     #             "dialogAction": {
#     #                 "type": "Delegate"
#     #             },
#     #             "intent": {
#     #                 'name':intent,
#     #                 'slots': slots
                    
#     #                 }
        
#     #         }
#     #     }
#     #         return response
    
#     # if event['invocationSource'] == 'FulfillmentCodeHook':
        
#     #     # Add order in Database
        
#     #     response = {
#     #     "sessionState": {
#     #         "dialogAction": {
#     #             "type": "Close"
#     #         },
#     #         "intent": {
#     #             'name':intent,
#     #             'slots': slots,
#     #             'state':'Fulfilled'
                
#     #             }
    
#     #     },
#     #     "messages": [
#     #         {
#     #             "contentType": "PlainText",
#     #             "content": "Thanks, I have placed your reservation"
#     #         }
#     #     ]
#     # }
            
#     #     return response