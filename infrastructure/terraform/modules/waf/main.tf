# WAF Web ACL
resource "aws_wafv2_web_acl" "main" {
  name        = "${var.project_name}-waf-${var.environment}"
  description = "WAF for ${var.project_name} ${var.environment} environment"
  scope       = var.waf_scope

  default_action {
    allow {}
  }

  # AWS Managed Rules - Common Rule Set
  rule {
    name     = "AWS-AWSManagedRulesCommonRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}AWSManagedRulesCommonRuleSet${var.environment}"
      sampled_requests_enabled   = true
    }
  }

  # AWS Managed Rules - Known Bad Inputs
  rule {
    name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}AWSManagedRulesKnownBadInputs${var.environment}"
      sampled_requests_enabled   = true
    }
  }

  # AWS Managed Rules - SQL Injection
  rule {
    name     = "AWS-AWSManagedRulesSQLiRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}AWSManagedRulesSQLi${var.environment}"
      sampled_requests_enabled   = true
    }
  }

  # Rate Limiting Rule
  rule {
    name     = "RateLimit"
    priority = 4

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = var.rate_limit
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}RateLimit${var.environment}"
      sampled_requests_enabled   = true
    }
  }

  # Custom Rule - Block common attack patterns
  rule {
    name     = "CustomBlockCommonAttacks"
    priority = 5

    action {
      block {}
    }

    statement {
      or_statement {
        statement {
          # Block requests with suspicious headers
          byte_match_statement {
            field_to_match {
              single_header {
                name = "user-agent"
              }
            }
            positional_constraint = "CONTAINS"
            search_string         = "sqlmap"
            text_transformation {
              priority = 1
              type     = "LOWERCASE"
            }
          }
        }

        statement {
          # Block directory traversal attempts
          byte_match_statement {
            field_to_match {
              uri_path {}
            }
            positional_constraint = "CONTAINS"
            search_string         = "../"
            text_transformation {
              priority = 1
              type     = "URL_DECODE"
            }
          }
        }

        statement {
          # Block script injection attempts
          byte_match_statement {
            field_to_match {
              query_string {}
            }
            positional_constraint = "CONTAINS"
            search_string         = "<script"
            text_transformation {
              priority = 1
              type     = "LOWERCASE"
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}CustomBlockCommonAttacks${var.environment}"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.project_name}WebACL${var.environment}"
    sampled_requests_enabled   = true
  }

  tags = {
    Name        = "${var.project_name}-waf-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# WAF Logging Configuration
resource "aws_wafv2_web_acl_logging_configuration" "main" {
  count = var.enable_logging ? 1 : 0

  resource_arn            = aws_wafv2_web_acl.main.arn
  log_destination_configs = var.log_destination_arn != "" ? [var.log_destination_arn] : []

  logging_filter {
    default_behavior = "KEEP"

    filter {
      behavior = "DROP"

      condition {
        action_condition {
          action = "ALLOW"
        }
      }

      requirement = "MEETS_ANY"
    }
  }
}

# CloudWatch Alarms for WAF
resource "aws_cloudwatch_metric_alarm" "waf_blocked_requests" {
  alarm_name          = "${var.project_name}-waf-blocked-requests-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "BlockedRequests"
  namespace           = "AWS/WAFV2"
  period              = "300"
  statistic           = "Sum"
  threshold           = "100"
  alarm_description   = "WAF has blocked a high number of requests"
  alarm_actions       = []

  dimensions = {
    WebACL = aws_wafv2_web_acl.main.name
    Region = data.aws_region.current.name
  }

  tags = {
    Name        = "${var.project_name}-waf-blocked-alarm-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Data source for current region
data "aws_region" "current" {}