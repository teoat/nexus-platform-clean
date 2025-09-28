output "endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
  sensitive   = true
}

output "port" {
  description = "Redis cluster port"
  value       = aws_elasticache_cluster.main.port
}

output "cluster_id" {
  description = "Redis cluster ID"
  value       = aws_elasticache_cluster.main.cluster_id
}

output "configuration_endpoint" {
  description = "Redis cluster configuration endpoint"
  value       = aws_elasticache_cluster.main.configuration_endpoint
}

output "subnet_group_name" {
  description = "ElastiCache subnet group name"
  value       = aws_elasticache_subnet_group.main.name
}

output "parameter_group_name" {
  description = "ElastiCache parameter group name"
  value       = aws_elasticache_parameter_group.main.name
}