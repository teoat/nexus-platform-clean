#!/bin/bash
# NEXUS Platform - Production Environment Setup Script
# Automated setup for production infrastructure

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_NAME="nexus-platform"
ENVIRONMENT="production"
AWS_REGION="us-east-1"
DOMAIN_NAME="nexusplatform.com"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root"
   exit 1
fi

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check required commands
    local required_commands=("aws" "kubectl" "helm" "terraform" "docker" "python3" "pip")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "Required command '$cmd' is not installed"
            exit 1
        fi
    done

    # Check AWS CLI configuration
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS CLI is not configured. Please run 'aws configure'"
        exit 1
    fi

    # Check Python version
    local python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$python_version < 3.9" | bc -l) -eq 1 ]]; then
        log_error "Python 3.9+ is required. Current version: $python_version"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."

    # Install Python dependencies
    pip install -r requirements.txt

    # Install additional production dependencies
    pip install gunicorn uvicorn[standard] psycopg2-binary redis cryptography boto3 hvac prometheus-client structlog

    # Install Helm charts
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update

    log_success "Dependencies installed"
}

# Setup AWS infrastructure
setup_aws_infrastructure() {
    log_info "Setting up AWS infrastructure..."

    # Create S3 bucket for Terraform state
    local state_bucket="${PROJECT_NAME}-terraform-state-$(date +%s)"
    aws s3 mb "s3://${state_bucket}" --region "$AWS_REGION"

    # Create S3 bucket for backups
    local backup_bucket="${PROJECT_NAME}-backups-$(date +%s)"
    aws s3 mb "s3://${backup_bucket}" --region "$AWS_REGION"

    # Enable versioning on buckets
    aws s3api put-bucket-versioning --bucket "$state_bucket" --versioning-configuration Status=Enabled
    aws s3api put-bucket-versioning --bucket "$backup_bucket" --versioning-configuration Status=Enabled

    # Create IAM role for EKS
    aws iam create-role \
        --role-name "${PROJECT_NAME}-eks-role" \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "eks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }' || log_warning "EKS role already exists"

    # Attach required policies
    aws iam attach-role-policy \
        --role-name "${PROJECT_NAME}-eks-role" \
        --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy

    # Create IAM role for EKS nodes
    aws iam create-role \
        --role-name "${PROJECT_NAME}-eks-node-role" \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }' || log_warning "EKS node role already exists"

    # Attach required policies for nodes
    local node_policies=(
        "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
        "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
        "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
    )

    for policy in "${node_policies[@]}"; do
        aws iam attach-role-policy \
            --role-name "${PROJECT_NAME}-eks-node-role" \
            --policy-arn "$policy" || log_warning "Policy $policy already attached"
    done

    log_success "AWS infrastructure setup completed"
}

# Deploy Terraform infrastructure
deploy_terraform() {
    log_info "Deploying Terraform infrastructure..."

    cd infrastructure/terraform

    # Initialize Terraform
    terraform init

    # Create terraform.tfvars
    cat > terraform.tfvars << EOF
aws_region = "$AWS_REGION"
project_name = "$PROJECT_NAME"
environment = "$ENVIRONMENT"
domain_name = "$DOMAIN_NAME"
database_password = "$(openssl rand -base64 32)"
redis_auth_token = "$(openssl rand -base64 32)"
EOF

    # Plan and apply
    terraform plan -out=tfplan
    terraform apply tfplan

    # Get outputs
    export EKS_CLUSTER_NAME=$(terraform output -raw cluster_name)
    export RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
    export REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)
    export ALB_DNS_NAME=$(terraform output -raw alb_dns_name)
    export S3_BACKUP_BUCKET=$(terraform output -raw s3_backup_bucket)

    cd ../..

    log_success "Terraform infrastructure deployed"
}

# Configure Kubernetes
configure_kubernetes() {
    log_info "Configuring Kubernetes..."

    # Update kubeconfig
    aws eks update-kubeconfig --region "$AWS_REGION" --name "$EKS_CLUSTER_NAME"

    # Create namespace
    kubectl apply -f k8s/manifests/namespace.yaml

    # Create secrets
    kubectl create secret generic nexus-secrets \
        --from-literal=database-username=nexus_admin \
        --from-literal=database-password="$(openssl rand -base64 32)" \
        --from-literal=redis-password="$(openssl rand -base64 32)" \
        --from-literal=jwt-secret-key="$(openssl rand -base64 32)" \
        --from-literal=encryption-key="$(openssl rand -base64 32)" \
        --from-literal=smtp-host=smtp.gmail.com \
        --from-literal=smtp-username=changeme \
        --from-literal=smtp-password=changeme \
        --from-literal=s3-backup-bucket="$S3_BACKUP_BUCKET" \
        --from-literal=s3-access-key=changeme \
        --from-literal=s3-secret-key=changeme \
        --from-literal=s3-region="$AWS_REGION" \
        -n nexus-platform

    # Create SSL certificates
    kubectl create secret tls nexus-ssl-certs \
        --cert=/etc/ssl/certs/nexus.crt \
        --key=/etc/ssl/private/nexus.key \
        -n nexus-platform || log_warning "SSL certificates not found, using self-signed"

    log_success "Kubernetes configured"
}

# Deploy applications
deploy_applications() {
    log_info "Deploying applications..."

    # Deploy backend
    kubectl apply -f k8s/manifests/backend-deployment.yaml

    # Deploy frontend
    kubectl apply -f k8s/manifests/frontend-deployment.yaml

    # Deploy nginx
    kubectl apply -f k8s/manifests/nginx-deployment.yaml

    # Wait for deployments
    kubectl rollout status deployment/nexus-backend -n nexus-platform --timeout=300s
    kubectl rollout status deployment/nexus-frontend -n nexus-platform --timeout=300s
    kubectl rollout status deployment/nexus-nginx -n nexus-platform --timeout=300s

    log_success "Applications deployed"
}

# Configure monitoring
configure_monitoring() {
    log_info "Configuring monitoring..."

    # Install Prometheus
    helm install prometheus prometheus-community/kube-prometheus-stack \
        --namespace nexus-platform \
        --create-namespace \
        --set grafana.adminPassword=admin123 \
        --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
        --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false

    # Wait for monitoring to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=prometheus -n nexus-platform --timeout=300s

    log_success "Monitoring configured"
}

# Run validation
run_validation() {
    log_info "Running validation..."

    # Run production validation
    python3 scripts/validate_production.py

    log_success "Validation completed"
}

# Main function
main() {
    log_info "Starting NEXUS Platform production environment setup..."

    # Check prerequisites
    check_prerequisites

    # Install dependencies
    install_dependencies

    # Setup AWS infrastructure
    setup_aws_infrastructure

    # Deploy Terraform infrastructure
    deploy_terraform

    # Configure Kubernetes
    configure_kubernetes

    # Deploy applications
    deploy_applications

    # Configure monitoring
    configure_monitoring

    # Run validation
    run_validation

    log_success "Production environment setup completed successfully!"

    # Display access information
    echo ""
    echo "=========================================="
    echo "NEXUS Platform Production Environment"
    echo "=========================================="
    echo "Application URL: https://$DOMAIN_NAME"
    echo "Grafana URL: https://$DOMAIN_NAME:3000"
    echo "Prometheus URL: https://$DOMAIN_NAME:9090"
    echo "Kubernetes Cluster: $EKS_CLUSTER_NAME"
    echo "AWS Region: $AWS_REGION"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Update DNS records to point to: $ALB_DNS_NAME"
    echo "2. Configure SSL certificates for production"
    echo "3. Set up monitoring alerts"
    echo "4. Configure backup schedules"
    echo "5. Run security audit"
    echo ""
}

# Run main function
main "$@"
