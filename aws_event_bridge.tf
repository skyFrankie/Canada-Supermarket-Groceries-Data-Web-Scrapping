#The time is counted in UTC
resource "aws_cloudwatch_event_rule" "scrap_trigger_lambda_event_rule" {
  name = "scrap_trigger_lambda_event_rule"
  description = "trigger supermarket data scrapping every Thursday"
  schedule_expression = "cron(0 13 ? * THU *)"
}

resource "aws_cloudwatch_event_target" "profile_generator_lambda_target" {
  arn = module.aws_lambda[var.scrap_trigger_lambda_name].lambda_arn
  rule = aws_cloudwatch_event_rule.scrap_trigger_lambda_event_rule.name
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_rw_fallout_retry_step_deletion_lambda" {
  statement_id = "AllowExecutionFromCloudWatch"
  action = "lambda:InvokeFunction"
  function_name = var.scrap_trigger_lambda_name
  principal = "events.amazonaws.com"
  source_arn = aws_cloudwatch_event_rule.scrap_trigger_lambda_event_rule.arn
}

resource "aws_cloudwatch_event_rule" "aws_batch_failure_event_rule" {
  name = "batch_scrap_failure_event_rule"
  description = "push notification if scrapping failed in batch"
  event_pattern = jsonencode({
    detail-type = [
      "Batch Job State Change"
    ],
    source = [
      "aws.batch"
    ],
    detail = {
      status = [
        "FAILED"
      ]
    }
  })
}

resource "aws_cloudwatch_event_target" "sns" {
  rule      = aws_cloudwatch_event_rule.aws_batch_failure_event_rule.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.batch_failure_notification.arn
}
