output "vpc_id" {
  description = "The ID of the custom VPC"
  value       = aws_vpc.main.id
}

output "public_subnets" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_app_subnets" {
  description = "IDs of the private app subnets"
  value       = aws_subnet.private_app[*].id
}

output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Route53 Zone ID of the ALB"
  value       = aws_lb.main.zone_id
}

output "rds_endpoint" {
  description = "Endpoint of the MySQL RDS instance"
  value       = aws_db_instance.mysql.endpoint
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.mysql.db_name
}

output "asg_name" {
  description = "Name of the EC2 Auto Scaling Group"
  value       = aws_autoscaling_group.app.name
}
