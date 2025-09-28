variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "nexus"
}

variable "ecs_cluster_name" {
  description = "ECS cluster name for monitoring"
  type        = string
}

variable "rds_instance_id" {
  description = "RDS instance ID for monitoring"
  type        = string
}

variable "alb_arn_suffix" {
  description = "ALB ARN suffix for monitoring"
  type        = string
}

variable "sns_topic_arn" {
  description = "SNS topic ARN for alarm notifications"
  type        = string
  default     = ""
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}