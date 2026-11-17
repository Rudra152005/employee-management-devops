variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "CIDR block for the custom VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "Public subnets CIDR list (across 2 AZs)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_app_subnets" {
  description = "Private App Subnets CIDR list for EC2 ASG"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "private_db_subnets" {
  description = "Private DB Subnets CIDR list for RDS Multi-AZ"
  type        = list(string)
  default     = ["10.0.20.0/24", "10.0.21.0/24"]
}

variable "instance_type" {
  description = "EC2 instance type for application nodes"
  type        = string
  default     = "t3.small"
}

variable "asg_min_size" {
  description = "Minimum size of Auto Scaling Group"
  type        = number
  default     = 2
}

variable "asg_max_size" {
  description = "Maximum size of Auto Scaling Group"
  type        = number
  default     = 4
}

variable "asg_desired_capacity" {
  description = "Desired capacity of Auto Scaling Group"
  type        = number
  default     = 2
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "MySQL database name"
  type        = string
  default     = "employeedb"
}

variable "db_username" {
  description = "MySQL administrator username"
  type        = string
  default     = "dbadmin"
}

variable "db_password" {
  description = "MySQL administrator password"
  type        = string
  sensitive   = true
  default     = "DevOpsMaster2026!"
}

variable "admin_cidr" {
  description = "Administrator CIDR for SSH bastion access"
  type        = string
  default     = "203.0.113.0/24"
}
