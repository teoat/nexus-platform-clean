# NEXUS Platform - Terraform Outputs
# Output values for NEXUS platform infrastructure

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnets
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "cluster_iam_role_name" {
  description = "IAM role name associated with the EKS cluster"
  value       = module.eks.cluster_iam_role_name
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN associated with the EKS cluster"
  value       = module.eks.cluster_iam_role_arn
}

output "db_instance_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_instance_endpoint
}

output "db_instance_id" {
  description = "RDS instance ID"
  value       = module.rds.db_instance_id
}

output "db_instance_arn" {
  description = "RDS instance ARN"
  value       = module.rds.db_instance_arn
}

output "db_instance_address" {
  description = "RDS instance address"
  value       = module.rds.db_instance_address
}

output "db_instance_port" {
  description = "RDS instance port"
  value       = module.rds.db_instance_port
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = module.redis.cluster_configuration_endpoint
}

output "redis_port" {
  description = "Redis cluster port"
  value       = module.redis.cluster_configuration_endpoint_port
}

output "redis_cluster_id" {
  description = "Redis cluster ID"
  value       = module.redis.cluster_id
}

# Kubernetes Configuration
output "kubeconfig" {
  description = "Kubeconfig for accessing the EKS cluster"
  value       = module.eks.kubeconfig
  sensitive   = true
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_arn" {
  description = "EKS cluster ARN"
  value       = module.eks.cluster_arn
}

# Security Groups
output "eks_security_group_id" {
  description = "EKS cluster security group ID"
  value       = module.eks.cluster_security_group_id
}

output "node_security_group_id" {
  description = "EKS node security group ID"
  value       = module.eks.node_security_group_id
}

# Subnet Information
output "database_subnets" {
  description = "Database subnet IDs"
  value       = module.vpc.database_subnets
}

output "database_subnet_group" {
  description = "Database subnet group name"
  value       = module.vpc.database_subnet_group
}

# Load Balancer
output "cluster_primary_security_group_id" {
  description = "Cluster primary security group ID"
  value       = module.eks.cluster_primary_security_group_id
}

# Monitoring
output "cluster_platform_version" {
  description = "Platform version of the EKS cluster"
  value       = module.eks.cluster_platform_version
}

output "cluster_status" {
  description = "Status of the EKS cluster"
  value       = module.eks.cluster_status
}
