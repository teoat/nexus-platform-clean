variable "domain_name" {
  description = "Primary domain name for the certificate"
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

variable "subject_alternative_names" {
  description = "List of subject alternative names for the certificate"
  type        = list(string)
  default     = []
}

variable "validation_method" {
  description = "Certificate validation method (DNS or EMAIL)"
  type        = string
  default     = "DNS"
}
