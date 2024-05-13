import os
from scrapper.LOBLAWS import LOBLAWSSCRAPPER
from scrapper.HMART import HMARTSCRAPPER
from scrapper.METRO import METROSCRAPPER
import yaml
from botocore.exceptions import ClientError
import traceback

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAP_S3_BUCKET_NAME = "groceries-app-scrap-data"

def upload_file_s3(s3, filepath, store):
   try:
      s3.upload_file(filepath, SCRAP_S3_BUCKET_NAME, f'{store}/'+filepath.split("/")[-1])
   except ClientError as e:
      print(traceback.format_exc())
      raise Exception(e)

def get_configuration():
    with open(os.path.join(ROOT_DIR, 'scrapper/webscrapper_config.yaml'), 'r') as stream:
        try:
            params = yaml.safe_load(stream)
            return params
        except yaml.YAMLError as exc:
            raise Exception(exc)

params = get_configuration()

scrap_map = {
    'Loblaws': LOBLAWSSCRAPPER(ROOT_DIR=ROOT_DIR, params=params),
    'HMart': HMARTSCRAPPER(ROOT_DIR=ROOT_DIR, params=params),
    'Metro': METROSCRAPPER(ROOT_DIR=ROOT_DIR, params=params)
}
