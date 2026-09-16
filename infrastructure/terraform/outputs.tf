output "alb_dns_name" {
  description = "Public DNS URL of the Application Load Balancer"
  value       = "http://${aws_lb.main.dns_name}"
}

output "vpc_id" {
  description = "VPC ID of the provisioned network"
  value       = aws_vpc.main.id
}

output "target_group_arn" {
  description = "Target Group ARN managing EC2 instances"
  value       = aws_lb_target_group.main.arn
}

output "asg_name" {
  description = "Auto Scaling Group Name"
  value       = aws_autoscaling_group.web.name
}
