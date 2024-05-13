######################################## Create S3 ##################################
resource "aws_s3_bucket" "scrap_data_bucket" {
  bucket = var.scrap_data_bucket
}

resource "aws_s3_bucket" "lambda_arti_bucket" {
  bucket = var.lambda_arti_bucket
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = var.data_processing_lambda_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.scrap_data_bucket.arn
  depends_on = [
    module.aws_lambda
  ]
}

resource "aws_s3_bucket_notification" "scrap_data_notification" {
  bucket = aws_s3_bucket.scrap_data_bucket.id
  lambda_function {
    id = "scrap_data_incoming"
    lambda_function_arn =  module.aws_lambda[var.data_processing_lambda_name].lambda_arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = ""
    filter_suffix       = ".csv"
  }
  depends_on = [
    module.aws_lambda,
    aws_s3_bucket.scrap_data_bucket
  ]
}
