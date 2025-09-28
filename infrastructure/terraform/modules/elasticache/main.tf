# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-redis-${var.environment}"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name        = "${var.project_name}-redis-subnet-group-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ElastiCache Parameter Group
resource "aws_elasticache_parameter_group" "main" {
  family = "redis7"
  name   = "${var.project_name}-redis-params-${var.environment}"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "tcp-keepalive"
    value = "300"
  }

  parameter {
    name  = "timeout"
    value = "300"
  }

  tags = {
    Name        = "${var.project_name}-redis-params-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ElastiCache Redis Cluster
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${var.project_name}-redis-${var.environment}"
  engine               = "redis"
  node_type            = var.cache_node_type
  num_cache_nodes      = var.cache_num_cache_nodes
  parameter_group_name = aws_elasticache_parameter_group.main.name
  engine_version       = var.cache_engine_version
  port                 = var.cache_port

  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [var.cache_security_group_id]

  maintenance_window         = var.cache_maintenance_window
  snapshot_window           = var.cache_snapshot_window
  snapshot_retention_limit  = var.cache_snapshot_retention_limit

  apply_immediately = false

  tags = {
    Name        = "${var.project_name}-redis-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# CloudWatch Alarms for ElastiCache
resource "aws_cloudwatch_metric_alarm" "cache_cpu_utilization" {
  alarm_name          = "${var.project_name}-redis-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "75"
  alarm_description   = "Redis cluster CPU utilization is too high"
  alarm_actions       = []

  dimensions = {
    CacheClusterId = aws_elasticache_cluster.main.cluster_id
  }

  tags = {
    Name        = "${var.project_name}-redis-cpu-alarm-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_cloudwatch_metric_alarm" "cache_memory_utilization" {
  alarm_name          = "${var.project_name}-redis-memory-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Redis cluster memory utilization is too high"
  alarm_actions       = []

  dimensions = {
    CacheClusterId = aws_elasticache_cluster.main.cluster_id
  }

  tags = {
    Name        = "${var.project_name}-redis-memory-alarm-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}
