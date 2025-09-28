# infrastructure/terraform/main.tf - Terraform Main Configuration
# This file defines the main infrastructure resources to be provisioned using Terraform.
# For more details, see: https://developer.hashicorp.com/terraform/language/syntax/configuration

provider "aws" {
  region = "us-east-1"
}

# Configure the Google Cloud provider (example)
# provider "google" {
#   project = "your-gcp-project-id"
#   region  = "us-central1"
# }

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true
  tags = {
    Name = "nexus-vpc"
  }
}

resource "aws_subnet" "public_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true
  tags = {
    Name = "nexus-public-a"
  }
}

resource "aws_subnet" "public_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = true
  tags = {
    Name = "nexus-public-b"
  }
}

resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "us-east-1a"
  tags = {
    Name = "nexus-private-a"
  }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "us-east-1b"
  tags = {
    Name = "nexus-private-b"
  }
}

# Example: Create a Kubernetes Cluster (EKS on AWS)
# resource "aws_eks_cluster" "nexus_cluster" {
#   name     = "nexus-eks-cluster"
#   role_arn = aws_iam_role.eks_cluster_role.arn
#   vpc_config {
#     subnet_ids = [
#       aws_subnet.private_a.id,
#       aws_subnet.private_b.id
#     ]
#   }
#   # ... other configurations
# }

# Example: Create an S3 bucket for static assets
# resource "aws_s3_bucket" "static_assets" {
#   bucket = "nexus-static-assets-${var.environment}"
#   acl    = "private"
#   versioning {
#     enabled = true
#   }
#   tags = {
#     Environment = var.environment
#     Project     = "Nexus"
#   }
# }

variable "environment" {
  description = "The deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

output "vpc_id" {
  description = "The ID of the main VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = [aws_subnet.public_a.id, aws_subnet.public_b.id]
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}
