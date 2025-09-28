# Route 53 Hosted Zone (data source - assumes it exists)
data "aws_route53_zone" "main" {
  name         = var.domain_name
  private_zone = false
}

# API DNS Record (points to ALB)
resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${var.api_subdomain}.${var.domain_name}"
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

# Frontend DNS Record (points to CloudFront)
resource "aws_route53_record" "app" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${var.app_subdomain}.${var.domain_name}"
  type    = "A"

  alias {
    name                   = var.cloudfront_domain_name
    zone_id                = var.cloudfront_zone_id
    evaluate_target_health = false
  }
}

# Root domain record (optional - points to frontend)
resource "aws_route53_record" "root" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = var.cloudfront_domain_name
    zone_id                = var.cloudfront_zone_id
    evaluate_target_health = false
  }
}

# Health Checks (optional)
resource "aws_route53_health_check" "api" {
  count = var.create_health_check ? 1 : 0

  fqdn              = "${var.api_subdomain}.${var.domain_name}"
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3
  request_interval  = 30

  tags = {
    Name        = "${var.project_name}-api-health-check-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_route53_health_check" "app" {
  count = var.create_health_check ? 1 : 0

  fqdn              = "${var.app_subdomain}.${var.domain_name}"
  port              = 443
  type              = "HTTPS"
  resource_path     = "/"
  failure_threshold = 3
  request_interval  = 30

  tags = {
    Name        = "${var.project_name}-app-health-check-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# CAA Records for SSL certificate validation
resource "aws_route53_record" "caa" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "CAA"
  ttl     = 300
  records = [
    "0 issue \"amazon.com\"",
    "0 issuewild \"amazon.com\"",
    "0 iodef \"mailto:security@${var.domain_name}\""
  ]
}

# TXT Record for domain verification (if needed)
resource "aws_route53_record" "txt_verification" {
  count = var.environment == "production" ? 1 : 0

  zone_id = data.aws_route53_zone.main.zone_id
  name    = "_nexus-verification.${var.domain_name}"
  type    = "TXT"
  ttl     = 300
  records = ["nexus-platform-verification-${var.environment}"]
}
