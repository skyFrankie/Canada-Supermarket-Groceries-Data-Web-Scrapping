import boto3
from botocore.exceptions import ClientError
import traceback
from store_mapping import mapping

#Different stores have different scrap mapping
def lambda_handler(event, context):
    try:
        batch_client = boto3.client('batch')
        params = mapping.get(event['store'], None)
        if not params:
            raise Exception('No store mapping found!')
        for i in params['loop_info']:
            params['params']['environment'][1]['value'] = f'{i}'
            job_response = batch_client.submit_job(
                jobName=f'daily_scrapping_{event["store"]}_{i}',
                jobQueue='groceries-app-scrap-job-queue',
                jobDefinition='groceries-app-scrap-job-definition',
                containerOverrides=params['params']
            )
            print(job_response)
        response = {
            "statusCode": 200,
            "body": 'Done'
        }

        return response
    except ClientError as e:
        print(traceback.format_exc())
        raise Exception(e)
