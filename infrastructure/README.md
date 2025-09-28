# NEXUS Infrastructure Documentation

This document provides an overview of the NEXUS infrastructure setup, including Terraform configurations, deployment procedures, and maintenance guidelines.

## Overview

The NEXUS infrastructure is managed using Infrastructure as Code (IaC) with Terraform. It includes cloud resources, Kubernetes clusters, databases, and monitoring systems.

## Directory Structure

```
infrastructure/
├── main.tf                 # Main Terraform configuration
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── terraform.tfvars        # Variable values
├── modules/                # Reusable Terraform modules
│   ├── vpc/
│   ├── eks/
│   ├── rds/
│   └── monitoring/
└── README.md               # This file
```

## Prerequisites

Before deploying the infrastructure, ensure you have:

- AWS CLI configured with appropriate credentials
- Terraform installed (version 1.0+)
- kubectl installed for Kubernetes management
- Helm installed for package management

## Quick Start

### 1. Initialize Terraform

```bash
cd infrastructure
terraform init
```

### 2. Plan the Deployment

```bash
terraform plan -var-file=terraform.tfvars
```

### 3. Apply the Configuration

```bash
terraform apply -var-file=terraform.tfvars
```

## Configuration

### Main Components

- **VPC**: Virtual Private Cloud with public and private subnets
- **EKS**: Amazon Elastic Kubernetes Service cluster
- **RDS**: Amazon Relational Database Service
- **Monitoring**: Prometheus, Grafana, and ELK stack

### Variables

Key variables in `terraform.tfvars`:

```hcl
aws_region = "us-east-1"
environment = "production"
cluster_name = "nexus-cluster"
instance_type = "t3.medium"
```

## Deployment

### Kubernetes Deployment

After Terraform deployment, deploy applications to EKS:

```bash
aws eks update-kubeconfig --region us-east-1 --name nexus-cluster
kubectl apply -f ../k8s/unified-manifests.yaml
```

### Database Setup

The RDS instance is automatically created. Connect using:

```bash
psql -h <rds-endpoint> -U admin -d nexus
```

## Monitoring

### Accessing Monitoring Dashboards

- **Grafana**: http://grafana.nexus.com (admin/admin)
- **Prometheus**: http://prometheus.nexus.com
- **Kibana**: http://kibana.nexus.com

### Key Metrics

- Cluster CPU and memory usage
- Application response times
- Database connection pools
- Network traffic

## Backup and Recovery

### Automated Backups

- RDS: Daily snapshots retained for 7 days
- EKS: Velero backups every 6 hours
- Configuration: Git-based version control

### Manual Backup

```bash
# Backup EKS cluster
velero backup create nexus-backup --include-namespaces nexus

# Backup database
aws rds create-db-snapshot --db-instance-identifier nexus-db --db-snapshot-identifier nexus-db-snapshot
```

### Recovery

```bash
# Restore EKS cluster
velero restore create --from-backup nexus-backup

# Restore database
aws rds restore-db-instance-from-snapshot --db-instance-identifier nexus-db-restored --db-snapshot-identifier nexus-db-snapshot
```

## Security

### Access Control

- IAM roles for AWS resources
- RBAC for Kubernetes
- Security groups for network isolation

### Secrets Management

- AWS Secrets Manager for sensitive data
- Kubernetes secrets for application configs
- Encrypted storage for backups

## Troubleshooting

### Common Issues

1. **Terraform Apply Fails**
   - Check AWS credentials
   - Verify variable values
   - Review Terraform state

2. **Kubernetes Pods Not Starting**
   - Check resource limits
   - Verify image availability
   - Review pod logs

3. **Database Connection Issues**
   - Verify security group rules
   - Check RDS instance status
   - Confirm connection string

### Support

For infrastructure issues, contact the DevOps team or check the monitoring dashboards for anomalies.

## Maintenance

### Regular Tasks

- Update Terraform configurations monthly
- Review and rotate secrets quarterly
- Test backup and recovery procedures annually
- Monitor resource utilization weekly

### Scaling

To scale the infrastructure:

1. Update instance types in `terraform.tfvars`
2. Run `terraform plan` and `terraform apply`
3. Monitor performance metrics post-scaling

## Cost Optimization

- Use reserved instances for stable workloads
- Implement auto-scaling for variable loads
- Regularly review and delete unused resources
- Monitor costs using AWS Cost Explorer

## Compliance

- All resources tagged for cost allocation
- Encrypted data at rest and in transit
- Regular security assessments
- Audit logs retained for 7 years
