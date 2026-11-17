# Look up latest Ubuntu 22.04 LTS AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# IAM Role for EC2 Systems Manager and CloudWatch
resource "aws_iam_role" "ec2" {
  name = "${var.environment}-ec2-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "cloudwatch" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${var.environment}-ec2-instance-profile"
  role = aws_iam_role.ec2.name
}

# EC2 Launch Template
resource "aws_launch_template" "app" {
  name_prefix   = "${var.environment}-app-"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  iam_instance_profile {
    arn = aws_iam_instance_profile.ec2.arn
  }

  network_interfaces {
    associate_public_ip_address = false
    security_groups             = [aws_security_group.ec2.id]
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -e
    exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

    echo "==> Updating system packages..."
    apt-get update -y
    apt-get install -y python3-pip python3-venv git nginx

    echo "==> Configuring application directory..."
    mkdir -p /opt/employee-app
    cd /opt/employee-app

    # Create Python virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Set up production environment configuration
    cat <<EOC > /opt/employee-app/.env
    FLASK_ENV=production
    DATABASE_URL=mysql+pymysql://${var.db_username}:${var.db_password}@${aws_db_instance.mysql.endpoint}/${var.db_name}?charset=utf8mb4
    SECRET_KEY=prod-secret-key-super-secure
    JWT_SECRET_KEY=prod-jwt-secret-key-super-secure
    PORT=5000
    EOC

    echo "==> Launching Gunicorn service on port 5000..."
  EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.environment}-app-asg-instance"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

# EC2 Auto Scaling Group across Private App Subnets
resource "aws_autoscaling_group" "app" {
  name_prefix         = "${var.environment}-app-asg-"
  vpc_zone_identifier = aws_subnet.private_app[*].id
  target_group_arns   = [aws_lb_target_group.app.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300

  min_size     = var.asg_min_size
  max_size     = var.asg_max_size
  desired_capacity = var.asg_desired_capacity

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.environment}-asg-node"
    propagate_at_launch = true
  }

  lifecycle {
    create_before_destroy = true
  }
}
