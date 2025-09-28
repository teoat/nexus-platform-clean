output "ecs_log_group_name" {
  description = "ECS CloudWatch log group name"
  value       = aws_cloudwatch_log_group.ecs_logs.name
}

output "alb_log_group_name" {
  description = "ALB CloudWatch log group name"
  value       = aws_cloudwatch_log_group.alb_logs.name
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alarms"
  value       = local.sns_topic_arn
}

output "dashboard_name" {
  description = "CloudWatch dashboard name"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}
