locals {
  frontend_bucket_name = var.frontend_bucket_name != "" ? var.frontend_bucket_name : "${var.project_name}-frontend-${var.environment}"
  logs_bucket_name     = var.logs_bucket_name != "" ? var.logs_bucket_name : "${var.project_name}-logs-${var.environment}"
  backups_bucket_name  = var.backups_bucket_name != "" ? var.backups_bucket_name : "${var.project_name}-backups-${var.environment}"
}

# Frontend Assets Bucket
resource "aws_s3_bucket" "frontend" {
  bucket = local.frontend_bucket_name

  tags = {
    Name        = local.frontend_bucket_name
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "frontend-assets"
  }
}

resource "aws_s3_bucket_versioning" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Logs Bucket
resource "aws_s3_bucket" "logs" {
  bucket = local.logs_bucket_name

  tags = {
    Name        = local.logs_bucket_name
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "logs"
  }
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Backups Bucket
resource "aws_s3_bucket" "backups" {
  bucket = local.backups_bucket_name

  tags = {
    Name        = local.backups_bucket_name
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "backups"
  }
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket = aws_s3_bucket.backups.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Lifecycle configuration for logs bucket
resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "log_expiration"
    status = "Enabled"

    expiration {
      days = 90
    }

    filter {
      prefix = "logs/"
    }
  }
}

# Lifecycle configuration for backups bucket
resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "backup_transition"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    filter {
      prefix = "backups/"
    }
  }
}
