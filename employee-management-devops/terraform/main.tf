# Root Module for Employee Management DevOps Architecture

locals {
  name_prefix = "${var.environment}-emp-mgmt"
}

# CloudWatch Log Group for Application Access Logs
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/ec2/${var.environment}-employee-app"
  retention_in_days = 30

  tags = {
    Name = "${var.environment}-cloudwatch-log-group"
  }
}
