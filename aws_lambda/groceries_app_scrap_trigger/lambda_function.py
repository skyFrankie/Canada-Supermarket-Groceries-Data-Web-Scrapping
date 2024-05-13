import boto3
import json

def lambda_handler(event, context):
    lambda_client = boto3.client('lambda')
    store_list = ['Loblaws', 'HMart', 'Metro']
    for store in store_list:
        response = lambda_client.invoke(
            FunctionName='groceries_app_scrap',
            InvocationType='Event',
            Payload=json.dumps(
                {'store': store}
            )
        )
    response = {
        "statusCode": 200,
        "body": 'Done'
    }

    return response