variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "nexus"
}

variable "frontend_bucket_name" {
  description = "Name of the S3 bucket for frontend assets"
  type        = string
  default     = ""
}

variable "logs_bucket_name" {
  description = "Name of the S3 bucket for logs"
  type        = string
  default     = ""
}

variable "backups_bucket_name" {
  description = "Name of the S3 bucket for backups"
  type        = string
  default     = ""
}

variable "enable_versioning" {
  description = "Enable versioning for S3 buckets"
  type        = bool
  default     = true
}

variable "force_destroy" {
  description = "Force destroy S3 buckets (use with caution)"
  type        = bool
  default     = false
}