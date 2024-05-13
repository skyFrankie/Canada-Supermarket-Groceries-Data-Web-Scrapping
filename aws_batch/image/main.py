import traceback
import boto3
import os
from utils import scrap_map, upload_file_s3

try:
    target_store = os.environ['STORE']
    scrapper = scrap_map[target_store]
    scrapper.scrap_main()
    s3_client = boto3.client('s3')
    upload_file_s3(s3_client, scrapper.output_filepath, target_store)
except Exception as e:
    print(traceback.format_exc())
    raise Exception(e)
