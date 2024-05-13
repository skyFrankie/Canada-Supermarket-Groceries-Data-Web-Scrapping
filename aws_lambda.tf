######################################## Create Lambda ##################################
module "aws_lambda"{
  source = "./tf_modules/aws_lambda"
  for_each = var.lambda_setting

  lambda_name = each.key
  lambda_arti_bucket = var.lambda_arti_bucket
  lambda_setting = each.value
  dynamodb_table_name = var.dynamodb_table_name
  depends_on = [
    aws_s3_bucket.lambda_arti_bucket
  ]
}
