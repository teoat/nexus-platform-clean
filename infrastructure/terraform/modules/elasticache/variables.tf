variable "vpc_id" {
  description = "VPC ID where ElastiCache will be deployed"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for ElastiCache"
  type        = list(string)
}

variable "cache_security_group_id" {
  description = "Security group ID for ElastiCache"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "nexus"
}

variable "cache_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "cache_num_cache_nodes" {
  description = "Number of cache nodes"
  type        = number
  default     = 1
}

variable "cache_engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.0"
}

variable "cache_port" {
  description = "Redis port"
  type        = number
  default     = 6379
}

variable "cache_parameter_group_name" {
  description = "Parameter group name for Redis"
  type        = string
  default     = "default.redis7"
}

variable "cache_maintenance_window" {
  description = "Maintenance window for ElastiCache"
  type        = string
  default     = "sun:05:00-sun:09:00"
}

variable "cache_snapshot_window" {
  description = "Snapshot window for ElastiCache"
  type        = string
  default     = "00:00-05:00"
}

variable "cache_snapshot_retention_limit" {
  description = "Snapshot retention limit in days"
  type        = number
  default     = 7
}
