output "web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = aws_wafv2_web_acl.main.arn
}

output "web_acl_id" {
  description = "ID of the WAF Web ACL"
  value       = aws_wafv2_web_acl.main.id
}

output "web_acl_capacity" {
  description = "Capacity of the WAF Web ACL"
  value       = aws_wafv2_web_acl.main.capacity
}