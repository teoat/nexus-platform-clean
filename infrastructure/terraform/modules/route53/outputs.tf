output "api_domain_name" {
  description = "API domain name"
  value       = aws_route53_record.api.name
}

output "app_domain_name" {
  description = "Frontend application domain name"
  value       = aws_route53_record.app.name
}

output "root_domain_name" {
  description = "Root domain name"
  value       = aws_route53_record.root.name
}

output "hosted_zone_id" {
  description = "Route 53 hosted zone ID"
  value       = data.aws_route53_zone.main.zone_id
}

output "hosted_zone_name" {
  description = "Route 53 hosted zone name"
  value       = data.aws_route53_zone.main.name
}