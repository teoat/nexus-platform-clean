variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "nexus"
}

variable "waf_scope" {
  description = "Scope of WAF (CLOUDFRONT or REGIONAL)"
  type        = string
  default     = "REGIONAL"
}

variable "rate_limit" {
  description = "Rate limit for requests per 5 minutes per IP"
  type        = number
  default     = 2000
}

variable "enable_logging" {
  description = "Enable WAF logging"
  type        = bool
  default     = true
}

variable "log_destination_arn" {
  description = "ARN of the log destination (Kinesis Firehose)"
  type        = string
  default     = ""
}
