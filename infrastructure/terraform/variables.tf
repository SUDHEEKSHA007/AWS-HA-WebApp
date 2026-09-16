variable "aws_region" {
  description = "AWS Region to deploy resources into"
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

variable "public_subnet_a_cidr" {
  description = "CIDR block for Public Subnet A"
  type        = string
  default     = "10.0.1.0/24"
}

variable "public_subnet_b_cidr" {
  description = "CIDR block for Public Subnet B"
  type        = string
  default     = "10.0.2.0/24"
}

variable "instance_type" {
  description = "EC2 Instance type (Free Tier eligible)"
  type        = string
  default     = "t2.micro"
}

variable "app_port" {
  description = "Application port Flask listens on"
  type        = number
  default     = 5000
}

variable "asg_min_size" {
  description = "Minimum number of EC2 instances in Auto Scaling Group"
  type        = number
  default     = 2
}

variable "asg_desired_size" {
  description = "Desired number of EC2 instances in Auto Scaling Group"
  type        = number
  default     = 2
}

variable "asg_max_size" {
  description = "Maximum number of EC2 instances in Auto Scaling Group"
  type        = number
  default     = 4
}
