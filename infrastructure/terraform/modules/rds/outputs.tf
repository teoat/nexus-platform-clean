output "instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.main.id
}

output "endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "address" {
  description = "RDS database address"
  value       = aws_db_instance.main.address
  sensitive   = true
}

output "port" {
  description = "RDS database port"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "RDS database name"
  value       = aws_db_instance.main.db_name
}

output "username" {
  description = "RDS database username"
  value       = aws_db_instance.main.username
  sensitive   = true
}

output "secret_arn" {
  description = "Secrets Manager secret ARN"
  value       = aws_secretsmanager_secret.db_password.arn
}

output "parameter_group_name" {
  description = "DB parameter group name"
  value       = aws_db_parameter_group.main.name
}

output "subnet_group_name" {
  description = "DB subnet group name"
  value       = aws_db_subnet_group.main.name
}
