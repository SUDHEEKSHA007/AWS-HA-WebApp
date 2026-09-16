# Fetch Available AZs in the current region
data "aws_availability_zones" "available" {
  state = "available"
}

# Fetch latest Ubuntu 24.04 LTS AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ==========================================
# 1. NETWORKING: VPC, Subnets, Gateway, Routes
# ==========================================

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.environment}-vpc"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.environment}-igw"
  }
}

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_a_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.environment}-public-subnet-a"
  }
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_b_cidr
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.environment}-public-subnet-b"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.environment}-public-rt"
  }
}

resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

# ==========================================
# 2. SECURITY GROUPS
# ==========================================

# ALB Security Group: Inbound Port 80 from Internet
resource "aws_security_group" "alb_sg" {
  name        = "${var.environment}-alb-sg"
  description = "Allow inbound HTTP from internet"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Outbound to all"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.environment}-alb-sg"
  }
}

# EC2 Security Group: Inbound Port 5000 ONLY from ALB
resource "aws_security_group" "ec2_sg" {
  name        = "${var.environment}-ec2-sg"
  description = "Allow application traffic strictly from ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Flask traffic strictly from ALB"
    from_port       = var.app_port
    to_port         = var.app_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  ingress {
    description = "SSH administrative access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Best practice: restrict to company VPN / My IP
  }

  egress {
    description = "Outbound to all"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.environment}-ec2-sg"
  }
}

# ==========================================
# 3. APPLICATION LOAD BALANCER & TARGET GROUP
# ==========================================

resource "aws_lb" "main" {
  name               = "${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_a.id, aws_subnet.public_b.id]

  tags = {
    Name = "${var.environment}-alb"
  }
}

resource "aws_lb_target_group" "main" {
  name     = "${var.environment}-tg"
  port     = var.app_port
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 15
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name = "${var.environment}-target-group"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}

# ==========================================
# 4. LAUNCH TEMPLATE & USER DATA BOOTSTRAP
# ==========================================

resource "aws_launch_template" "web" {
  name_prefix   = "${var.environment}-launch-template-"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.ec2_sg.id]
  }

  user_data = base64encode(<<-EOF
              #!/bin/bash
              set -e
              apt-get update -y
              apt-get install -y python3-pip python3-venv git

              # Clone repository
              cd /opt
              git clone https://github.com/SUDHEEKSHA007/AWS-HA-WebApp.git
              cd AWS-HA-WebApp

              # Setup Virtual Environment
              python3 -m venv .venv
              ./.venv/bin/pip install -r app/requirements.txt

              # Create systemd background service
              cat << 'SERVICE' > /etc/systemd/system/webapp.service
              [Unit]
              Description=AWS Highly Available Web Application
              After=network.target

              [Service]
              User=root
              WorkingDirectory=/opt/AWS-HA-WebApp
              ExecStart=/opt/AWS-HA-WebApp/.venv/bin/python app/app.py
              Restart=always
              RestartSec=5
              Environment=PORT=5000

              [Install]
              WantedBy=multi-user.target
              SERVICE

              systemctl daemon-reload
              systemctl enable --now webapp.service
              EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.environment}-web-asg-node"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

# ==========================================
# 5. AUTO SCALING GROUP (MULTI-AZ)
# ==========================================

resource "aws_autoscaling_group" "web" {
  name_prefix         = "${var.environment}-asg-"
  vpc_zone_identifier = [aws_subnet.public_a.id, aws_subnet.public_b.id]
  target_group_arns   = [aws_lb_target_group.main.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300

  min_size     = var.asg_min_size
  desired_capacity = var.asg_desired_size
  max_size     = var.asg_max_size

  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

# ==========================================
# 6. CLOUDWATCH ALARM
# ==========================================

resource "aws_cloudwatch_metric_alarm" "low_healthy_hosts" {
  alarm_name          = "${var.environment}-alb-low-healthy-hosts"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = 2
  alarm_description   = "Triggered if HealthyHostCount drops below 2 in Target Group"

  dimensions = {
    TargetGroup  = aws_lb_target_group.main.arn_suffix
    LoadBalancer = aws_lb.main.arn_suffix
  }
}
