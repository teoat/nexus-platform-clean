# NEXUS Platform - Local Development Infrastructure
# Simplified configuration for local development and testing

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Local values
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# VPC Module
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-${var.environment}-vpc"
  cidr = var.vpc_cidr

  azs             = slice(data.aws_availability_zones.available.names, 0, 2)
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
  database_subnets = var.database_subnet_cidrs

  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = local.common_tags
}

# Security Groups
resource "aws_security_group" "nexus_alb" {
  name_prefix = "${var.project_name}-${var.environment}-alb-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-alb-sg"
  })
}

resource "aws_security_group" "nexus_rds" {
  name_prefix = "${var.project_name}-${var.environment}-rds-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.nexus_ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  })
}

resource "aws_security_group" "nexus_redis" {
  name_prefix = "${var.project_name}-${var.environment}-redis-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.nexus_ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-redis-sg"
  })
}

resource "aws_security_group" "nexus_ecs" {
  name_prefix = "${var.project_name}-${var.environment}-ecs-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.nexus_alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-ecs-sg"
  })
}

# RDS Database
resource "random_password" "db_password" {
  length  = 16
  special = true
}

resource "aws_db_subnet_group" "nexus_db_subnet_group" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = module.vpc.database_subnets

  tags = local.common_tags
}

resource "aws_db_instance" "nexus_db" {
  identifier = "${var.project_name}-${var.environment}-db"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "nexus_platform"
  username = "nexus_admin"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.nexus_rds.id]
  db_subnet_group_name   = aws_db_subnet_group.nexus_db_subnet_group.name

  backup_retention_period = var.db_backup_retention_period
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = true
  deletion_protection = false

  tags = local.common_tags
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "nexus_redis_subnet_group" {
  name       = "${var.project_name}-${var.environment}-redis-subnet-group"
  subnet_ids = module.vpc.database_subnets
}

resource "aws_elasticache_replication_group" "nexus_redis" {
  replication_group_id       = "${var.project_name}-${var.environment}-redis"
  description                = "Redis cluster for Nexus Platform"

  node_type                  = var.redis_node_type
  port                       = 6379
  parameter_group_name       = "default.redis7"

  num_cache_clusters         = var.redis_num_cache_nodes

  subnet_group_name          = aws_elasticache_subnet_group.nexus_redis_subnet_group.name
  security_group_ids         = [aws_security_group.nexus_redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = local.common_tags
}

# Application Load Balancer
resource "aws_lb" "nexus_alb" {
  name               = "${var.project_name}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.nexus_alb.id]
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = false

  tags = local.common_tags
}

# ALB Target Group
resource "aws_lb_target_group" "nexus_tg" {
  name     = "${var.project_name}-${var.environment}-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = local.common_tags
}

# ALB Listener
resource "aws_lb_listener" "nexus_listener" {
  load_balancer_arn = aws_lb.nexus_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.nexus_tg.arn
  }
}

# S3 Bucket for Backups
resource "aws_s3_bucket" "nexus_backups" {
  bucket = "${var.project_name}-${var.environment}-backups-${random_string.bucket_suffix.result}"

  tags = local.common_tags
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_versioning" "nexus_backups_versioning" {
  bucket = aws_s3_bucket.nexus_backups.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "nexus_backups_encryption" {
  bucket = aws_s3_bucket.nexus_backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

output "database_subnets" {
  description = "List of IDs of database subnets"
  value       = module.vpc.database_subnets
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.nexus_db.endpoint
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.nexus_db.port
}

output "rds_db_name" {
  description = "RDS database name"
  value       = aws_db_instance.nexus_db.db_name
}

output "rds_username" {
  description = "RDS instance root username"
  value       = aws_db_instance.nexus_db.username
}

output "rds_password" {
  description = "RDS instance root password"
  value       = aws_db_instance.nexus_db.password
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_replication_group.nexus_redis.primary_endpoint_address
}

output "redis_port" {
  description = "Redis cluster port"
  value       = aws_elasticache_replication_group.nexus_redis.port
}

output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.nexus_alb.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.nexus_alb.zone_id
}

output "s3_bucket_id" {
  description = "S3 bucket ID"
  value       = aws_s3_bucket.nexus_backups.id
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.nexus_backups.arn
}
