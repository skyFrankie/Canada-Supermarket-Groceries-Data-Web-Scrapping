lambda_arti_bucket = "groceries-app-lambda-artifact"
scrap_data_bucket = "groceries-app-scrap-data"
region_name = "us-east-1"
dynamodb_table_name = "WebScrappingData"

lambda_setting = {
    groceries_app_data_processing = {
        lambda_description = "A lambda function that responsible for scrapped data processing"
        memory_size = 640
        timeout = 60
        lambda_layer_arn   = ["arn:aws:lambda:us-east-1::layer:AWSSDKPandas-Python39:1"]
        iam_service = ["lambda.amazonaws.com"]
    },
    groceries_app_scrap = {
        lambda_description = "A lambda function that trigger AWS batch job for its responsible superstore"
        memory_size = 640
        timeout = 60
        lambda_layer_arn   = null
        iam_service = ["lambda.amazonaws.com"]
    },
    groceries_app_scrap_trigger = {
        lambda_description = "A lambda function that trigger Lambdas which are responsible for scrapping"
        memory_size = 640
        timeout = 60
        lambda_layer_arn   = null
        iam_service = ["lambda.amazonaws.com"]
    }
}
