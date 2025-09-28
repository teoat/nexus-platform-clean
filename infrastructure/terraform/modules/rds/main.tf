# RDS PostgreSQL Module for NEXUS Platform

resource "aws_db_subnet_group" "main" {
  name       = "nexus-${var.environment}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "nexus-${var.environment}-db-subnet-group"
  }
}

resource "aws_db_parameter_group" "main" {
  family = "postgres15"
  name   = "nexus-${var.environment}-db-parameter-group"

  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }

  parameter {
    name  = "pg_stat_statements.track"
    value = "all"
  }

  parameter {
    name  = "pg_stat_statements.max"
    value = "10000"
  }

  parameter {
    name  = "track_activity_query_size"
    value = "4096"
  }

  tags = {
    Name = "nexus-${var.environment}-db-parameter-group"
  }
}

resource "aws_db_instance" "main" {
  identifier = "nexus-${var.environment}-db"

  # Engine configuration
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class

  # Storage configuration
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id           = aws_kms_key.rds.arn

  # Database configuration
  db_name  = "nexus"
  username = "nexus_admin"
  password = random_password.db_password.result
  port     = 5432

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.database_security_group_id]
  publicly_accessible    = false
  multi_az              = true

  # Backup configuration
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  copy_tags_to_snapshot  = true
  skip_final_snapshot    = false
  final_snapshot_identifier = "nexus-${var.environment}-db-final-snapshot"

  # Monitoring configuration
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_enhanced_monitoring.arn

  # Performance insights
  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.rds.arn
  performance_insights_retention_period = 7

  # Parameter group
  parameter_group_name = aws_db_parameter_group.main.name

  # Auto minor version upgrade
  auto_minor_version_upgrade = true

  # Deletion protection
  deletion_protection = var.deletion_protection

  tags = {
    Name = "nexus-${var.environment}-db"
  }

  depends_on = [
    aws_iam_role_policy_attachment.rds_enhanced_monitoring,
    aws_kms_key.rds
  ]
}

# KMS key for RDS encryption
resource "aws_kms_key" "rds" {
  description             = "KMS key for NEXUS RDS encryption"
  deletion_window_in_days = 30

  tags = {
    Name = "nexus-${var.environment}-rds-kms-key"
  }
}

resource "aws_kms_alias" "rds" {
  name          = "alias/nexus-${var.environment}-rds"
  target_key_id = aws_kms_key.rds.key_id
}

# Random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store password in Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "nexus/${var.environment}/database/password"
  description             = "NEXUS database password"
  kms_key_id              = aws_kms_key.rds.arn
  recovery_window_in_days = 0

  tags = {
    Name = "nexus-${var.environment}-db-password"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = aws_db_instance.main.username
    password = random_password.db_password.result
    host     = aws_db_instance.main.address
    port     = aws_db_instance.main.port
    dbname   = aws_db_instance.main.db_name
  })
}

# IAM role for enhanced monitoring
resource "aws_iam_role" "rds_enhanced_monitoring" {
  name = "nexus-${var.environment}-rds-enhanced-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "nexus-${var.environment}-rds-enhanced-monitoring"
  }
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudWatch alarms for RDS
resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  alarm_name          = "nexus-${var.environment}-db-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Database CPU utilization is above 80%"
  alarm_actions       = [var.sns_topic_arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = {
    Name = "nexus-${var.environment}-db-cpu-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "database_memory" {
  alarm_name          = "nexus-${var.environment}-db-free-memory"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "128000000" # 128 MB
  alarm_description   = "Database freeable memory is below 128MB"
  alarm_actions       = [var.sns_topic_arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = {
    Name = "nexus-${var.environment}-db-memory-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "database_connections" {
  alarm_name          = "nexus-${var.environment}-db-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Database connections are above 80% of maximum"
  alarm_actions       = [var.sns_topic_arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = {
    Name = "nexus-${var.environment}-db-connections-alarm"
  }
}
