# DB Subnet Group across Private DB Subnets
resource "aws_db_subnet_group" "rds" {
  name        = "${var.environment}-rds-subnet-group"
  subnet_ids  = aws_subnet.private_db[*].id
  description = "Subnet group for Employee Management RDS"

  tags = {
    Name = "${var.environment}-rds-subnet-group"
  }
}

# DB Parameter Group for UTF8MB4
resource "aws_db_parameter_group" "rds" {
  name   = "${var.environment}-mysql8-params"
  family = "mysql8.0"

  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }

  parameter {
    name  = "collation_server"
    value = "utf8mb4_unicode_ci"
  }
}

# Amazon RDS MySQL Instance (Multi-AZ)
resource "aws_db_instance" "mysql" {
  identifier             = "${var.environment}-employee-mysql"
  allocated_storage      = 20
  max_allocated_storage  = 100
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = var.db_instance_class
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  parameter_group_name   = aws_db_parameter_group.rds.name
  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  multi_az               = true
  storage_type           = "gp3"
  storage_encrypted      = true
  publicly_accessible    = false
  skip_final_snapshot    = true
  deletion_protection    = false

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "Sun:04:30-Sun:05:30"

  tags = {
    Name = "${var.environment}-employee-rds"
  }
}
