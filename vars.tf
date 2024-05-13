variable "lambda_arti_bucket" {
  description = "The name of bucket that store the lambda artifact"
  type        = string
}

variable "dynamodb_table_name" {
  description = "The name of table in dynamodb that store the scrapped data"
  type        = string
}

variable "lambda_setting" {
  description = "Setting for lambda"
  type        = map(
    object({
        lambda_description = string
        memory_size = number
        timeout = number
        lambda_layer_arn = list(string)
        iam_service = list(string)
    })
  )
}

variable "scrap_data_bucket" {
  description = "The name of the S3 bucket"
  type        = string
  default     = "groceries-app-daily-scrap"
}

variable "data_processing_lambda_name" {
  description = "The name of the Lambda responsible for scrap data processing"
  type = string
  default = "groceries_app_data_processing"
}

variable "scrap_trigger_lambda_name" {
  description = "The name of the Lambda responsible for scrap data processing"
  type = string
  default = "groceries_app_scrap_trigger"
}

variable "region_name" {
  type = string
}

