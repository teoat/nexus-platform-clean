# ALB Module for NEXUS Platform

resource "aws_lb" "main" {
  name               = "nexus-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.security_group_id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = var.deletion_protection

  tags = {
    Name = "nexus-${var.environment}-alb"
  }
}

resource "aws_lb_target_group" "main" {
  name        = "nexus-${var.environment}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

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

  stickiness {
    type            = "lb_cookie"
    cookie_duration = 1800
    enabled         = true
  }

  tags = {
    Name = "nexus-${var.environment}-target-group"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}

# WAF Association
resource "aws_wafregional_web_acl_association" "main" {
  resource_arn = aws_lb.main.arn
  web_acl_id   = var.web_acl_id
}

# CloudWatch Alarms for ALB
resource "aws_cloudwatch_metric_alarm" "alb_healthy_hosts" {
  alarm_name          = "nexus-${var.environment}-alb-healthy-hosts"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "Number of healthy hosts is below 1"
  alarm_actions       = [var.sns_topic_arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.main.arn_suffix
  }

  tags = {
    Name = "nexus-${var.environment}-alb-healthy-hosts-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_target_response_time" {
  alarm_name          = "nexus-${var.environment}-alb-response-time"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "2"
  alarm_description   = "Target response time is above 2 seconds"
  alarm_actions       = [var.sns_topic_arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  tags = {
    Name = "nexus-${var.environment}-alb-response-time-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_http_5xx" {
  alarm_name          = "nexus-${var.environment}-alb-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "Number of 5XX errors is above 10"
  alarm_actions       = [var.sns_topic_arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  tags = {
    Name = "nexus-${var.environment}-alb-5xx-alarm"
  }
}
