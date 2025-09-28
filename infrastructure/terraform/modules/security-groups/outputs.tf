output "alb_security_group_id" {
  description = "ALB security group ID"
  value       = aws_security_group.alb.id
}

output "ecs_security_group_id" {
  description = "ECS security group ID"
  value       = aws_security_group.ecs.id
}

output "database_security_group_id" {
  description = "Database security group ID"
  value       = aws_security_group.database.id
}

output "cache_security_group_id" {
  description = "Cache security group ID"
  value       = aws_security_group.cache.id
}

output "bastion_security_group_id" {
  description = "Bastion host security group ID"
  value       = aws_security_group.bastion.id
}

output "monitoring_security_group_id" {
  description = "Monitoring security group ID"
  value       = aws_security_group.monitoring.id
}
