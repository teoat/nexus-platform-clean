variable "domain_name" {
  description = "Primary domain name"
  type        = string
}

variable "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  type        = string
}

variable "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  type        = string
}

variable "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  type        = string
}

variable "cloudfront_zone_id" {
  description = "Zone ID of the CloudFront distribution"
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

variable "api_subdomain" {
  description = "Subdomain for API endpoints"
  type        = string
  default     = "api"
}

variable "app_subdomain" {
  description = "Subdomain for frontend application"
  type        = string
  default     = "app"
}

variable "create_health_check" {
  description = "Whether to create Route 53 health checks"
  type        = bool
  default     = true
}
