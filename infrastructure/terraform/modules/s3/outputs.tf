output "frontend_bucket_name" {
  description = "Name of the frontend assets S3 bucket"
  value       = aws_s3_bucket.frontend.bucket
}

output "frontend_bucket_domain_name" {
  description = "Domain name of the frontend assets S3 bucket"
  value       = aws_s3_bucket.frontend.bucket_domain_name
}

output "frontend_bucket_arn" {
  description = "ARN of the frontend assets S3 bucket"
  value       = aws_s3_bucket.frontend.arn
}

output "logs_bucket_name" {
  description = "Name of the logs S3 bucket"
  value       = aws_s3_bucket.logs.bucket
}

output "logs_bucket_arn" {
  description = "ARN of the logs S3 bucket"
  value       = aws_s3_bucket.logs.arn
}

output "backups_bucket_name" {
  description = "Name of the backups S3 bucket"
  value       = aws_s3_bucket.backups.bucket
}

output "backups_bucket_arn" {
  description = "ARN of the backups S3 bucket"
  value       = aws_s3_bucket.backups.arn
}
