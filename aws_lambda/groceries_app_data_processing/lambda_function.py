import pandas as pd
import boto3
import traceback
import json
from decimal import Decimal
from data_processor.DATAPROCESSOR import DATAPROCESSOR
import os

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        print(event)
        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        s3_file_name = event['Records'][0]['s3']['object']['key']
        output_filepath = f'/tmp/{s3_file_name.split("/")[-1]}'
        obj = s3_client.get_object(Bucket=bucket_name, Key=s3_file_name)
        df = pd.read_csv(obj['Body'])
        store_name = s3_file_name.split("/")[0]
        table_name = os.environ['dynamodb_tb_name']
        # cleansing
        df = DATAPROCESSOR(
            store=store_name,
            df=df
        ).data_cleansing()
        # Output
        df.to_csv(output_filepath, index=False)
        dynamodb = boto3.resource('dynamodb')
        output_json = json.loads(
            pd.read_csv(output_filepath).to_json(orient='records'),
            parse_float=Decimal
        )
        dynamoTable = dynamodb.Table(table_name)
        for record in output_json:
            dynamoTable.put_item(Item=record)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
