# Retrieves the default vpc for this region
data "aws_vpc" "default" {
  default = true
}

# Retrieves the subnet ids in the default vpc
data "aws_subnets" "all_default_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "batch" {
  name   = "batch"
  vpc_id = data.aws_vpc.default.id
  description = "batch VPC security group"

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = [
      "0.0.0.0/0",
    ]
  }
}

# Batch Service Role
resource "aws_iam_role" "aws_batch_service_role" {
  name = "groceries_app_batch_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Action": "sts:AssumeRole",
    "Effect": "Allow",
    "Principal": {
      "Service": "batch.amazonaws.com"
    }
  }]
}
EOF
}

resource "aws_iam_role_policy_attachment" "aws_batch_service_role" {
  role       = aws_iam_role.aws_batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

# ECS Task Execution Role
resource "aws_iam_role" "aws_ecs_task_execution_role" {
  name = "groceries-app-ecs-task-execution-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "aws_ecs_task_execution_role" {
  role       = aws_iam_role.aws_ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "batch_policy" {
  name = "aws_batch_s3_role"
  description = "Policy for aws batch upload scrap data to S3"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
      {
          "Action": [
            "s3:*"
          ],
          "Resource": "*",
          "Effect": "Allow"
      }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "aws_ecs_upload_s3_role" {
  role       = aws_iam_role.aws_ecs_task_execution_role.name
  policy_arn = aws_iam_policy.batch_policy.arn
}

resource "aws_batch_compute_environment" "batch" {
  compute_environment_name = "groceries-app-compute-env"

  compute_resources {
    max_vcpus = 256
    security_group_ids = [
      aws_security_group.batch.id,
    ]
    subnets = data.aws_subnets.all_default_subnets.ids
    type = "FARGATE"
  }
  service_role = aws_iam_role.aws_batch_service_role.arn
  type         = "MANAGED"
  depends_on = [
    aws_iam_role_policy_attachment.aws_batch_service_role
  ]
}

resource "aws_batch_job_queue" "batch" {
  name     = "groceries-app-scrap-job-queue"
  state    = "ENABLED"
  priority = "0"
  compute_environments = [
    aws_batch_compute_environment.batch.arn,
  ]
}

resource "aws_batch_job_definition" "batch" {
  name = "groceries-app-scrap-job-definition"
  type = "container"
  retry_strategy {
    attempts = 3
    evaluate_on_exit {
      action = "RETRY"
      on_exit_code = "*"
      on_reason = "*"
      on_status_reason = "*"
    }
  }
  timeout {
    attempt_duration_seconds = 10800
  }
  platform_capabilities = [
    "FARGATE",
  ]
  container_properties = jsonencode({
    command = ["./main.sh"]
    image   = ".dkr.ecr.${var.region_name}.amazonaws.com/groceries_app:latest"
    jobRoleArn = aws_iam_role.aws_ecs_task_execution_role.arn
    executionRoleArn = aws_iam_role.aws_ecs_task_execution_role.arn
    fargatePlatformConfiguration = {
      platformVersion = "LATEST"
    }
    runtimePlatform = {
      "operatingSystemFamily": "LINUX",
      "cpuArchitecture": "x86"
    }
    networkConfiguration = {
      assignPublicIp = "ENABLED"
    }
    resourceRequirements = [
      {
        type  = "VCPU"
        value = "1"
      },
      {
        type  = "MEMORY"
        value = "3072"
      }
    ]
  })
}
