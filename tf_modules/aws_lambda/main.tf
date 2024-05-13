variable "lambda_setting" {
  type = object({
    lambda_description = string
    memory_size = number
    timeout = number
    lambda_layer_arn = list(string)
    iam_service = list(string)
  })
}

variable "dynamodb_table_name" {
  description = "The name of table in dynamodb that store the scrapped data"
  type        = string
}

variable "lambda_name" {
  description = "The name of lambda"
  type        = string
}

variable "lambda_arti_bucket" {
  description = "The name of bucket that store the lambda artifact"
  type        = string
}

# Zip the Lamda function on the fly
data "archive_file" "lambda_source_code" {
  type        = "zip"
  source_dir  = "./aws_lambda/${var.lambda_name}/"
  output_path = "./aws_lambda/${var.lambda_name}.zip"
}

#Upload the zipped file to s3
resource "aws_s3_object" "upload_s3" {
  bucket = var.lambda_arti_bucket
  key    = "${var.lambda_name}/${var.lambda_name}.zip"
  source = "${data.archive_file.lambda_source_code.output_path}" # its mean it depended on zip
  source_hash = "${data.archive_file.lambda_source_code.output_base64sha256}"
}

#Read assume role template
data "template_file" "assume_role" {
  template = "${file("${path.module}/iam_policy/assume_role.json")}"
  vars = {
    iam_service = "${jsonencode(var.lambda_setting.iam_service)}"
  }
}

#Create IAM role with the assume role
resource "aws_iam_role" "lambda_role" {
  name = var.lambda_name
  assume_role_policy = "${data.template_file.assume_role.rendered}"
}

#Read the Lambda service requirements template
data "template_file" "iam_policy" {
  template = "${file("${path.module}/iam_policy/${var.lambda_name}.json")}"
}

#Create IAM policy for the Lambda IAM role
resource "aws_iam_policy" "policy" {
  name = var.lambda_name
  description = "Policy for ${var.lambda_name}"

  policy = "${data.template_file.iam_policy.rendered}"
}

#Attach the created IAM policy above to the IAM role
resource "aws_iam_policy_attachment" "policy_attachment" {
  name       = "${var.lambda_name}-attachment"
  roles      = ["${var.lambda_name}"]
  policy_arn = "${aws_iam_policy.policy.arn}"
}

#Create Lambda function
resource "aws_lambda_function" "lambda_function" {
  function_name = var.lambda_name

  description   = var.lambda_setting.lambda_description
  # Artifacts bucket
  s3_bucket = var.lambda_arti_bucket
  s3_key    = aws_s3_object.upload_s3.key
  memory_size = var.lambda_setting.memory_size
  timeout     = var.lambda_setting.timeout

  handler = "lambda_function.lambda_handler"
  runtime = "python3.9"
  environment {
    variables = {
      dynamodb_tb_name = var.dynamodb_table_name
    }
  }
  layers = var.lambda_setting.lambda_layer_arn
  role    = aws_iam_role.lambda_role.arn
  source_code_hash = "${data.archive_file.lambda_source_code.output_base64sha256}"
}

output "lambda_arn" {
  value = aws_lambda_function.lambda_function.arn
}