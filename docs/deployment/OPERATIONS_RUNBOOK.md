# Nexus Platform Operations Runbook

## Table of Contents

1. [Emergency Procedures](#emergency-procedures)
2. [Service Management](#service-management)
3. [Monitoring and Alerting](#monitoring-and-alerting)
4. [Backup and Recovery](#backup-and-recovery)
5. [Security Operations](#security-operations)
6. [Performance Optimization](#performance-optimization)
7. [Incident Response](#incident-response)
8. [Maintenance Procedures](#maintenance-procedures)

## Emergency Procedures

### Service Down - Immediate Response

#### 1. Check Service Status (0-5 minutes)

```bash
# Check ECS service status
aws ecs describe-services \
  --cluster nexus-platform-production-cluster \
  --services nexus-platform-production-service \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}'

# Check load balancer health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/nexus-platform-production-tg/1234567890123456

# Check recent events
aws ecs describe-services \
  --cluster nexus-platform-production-cluster \
  --services nexus-platform-production-service \
  --query 'services[0].events[0:5]'
```

#### 2. Restart Service (5-10 minutes)

```bash
# Force new deployment
aws ecs update-service \
  --cluster nexus-platform-production-cluster \
  --service nexus-platform-production-service \
  --force-new-deployment

# Wait for deployment to complete
aws ecs wait services-stable \
  --cluster nexus-platform-production-cluster \
  --services nexus-platform-production-service
```

#### 3. Check Application Logs (10-15 minutes)

```bash
# Get recent error logs
aws logs filter-log-events \
  --log-group-name /aws/ecs/nexus-platform-production \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "ERROR"

# Get application logs
aws logs tail /aws/ecs/nexus-platform-production --since 1h
```

#### 4. Escalate if Needed (15+ minutes)

- Contact on-call engineer
- Create incident ticket
- Notify stakeholders

### Database Issues

#### 1. Database Connection Problems

```bash
# Check RDS status
aws rds describe-db-instances \
  --db-instance-identifier nexus-platform-production-db \
  --query 'DBInstances[0].{Status:DBInstanceStatus,Endpoint:Endpoint.Address}'

# Test connection
nc -zv $RDS_ENDPOINT 5432

# Check connection logs
aws logs filter-log-events \
  --log-group-name /aws/rds/instance/nexus-platform-production-db/error \
  --start-time $(date -d '1 hour ago' +%s)000
```

#### 2. Database Performance Issues

```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=nexus-platform-production-db \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

#### 3. Database Recovery

```bash
# List available snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier nexus-platform-production-db \
  --query 'DBSnapshots[?Status==`available`]'

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier nexus-platform-recovery-db \
  --db-snapshot-identifier nexus-platform-production-db-2024-01-01-12-00
```

### Load Balancer Issues

#### 1. Health Check Failures

```bash
# Check target group health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/nexus-platform-production-tg/1234567890123456

# Check health check configuration
aws elbv2 describe-target-groups \
  --target-group-arns arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/nexus-platform-production-tg/1234567890123456 \
  --query 'TargetGroups[0].HealthCheck'
```

#### 2. SSL Certificate Issues

```bash
# Check certificate status
aws acm list-certificates \
  --query 'CertificateSummaryList[?DomainName==`your-domain.com`]'

# Check certificate details
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012
```

## Service Management

### Starting Services

#### 1. Start ECS Service

```bash
# Start service
aws ecs update-service \
  --cluster nexus-platform-production-cluster \
  --service nexus-platform-production-service \
  --desired-count 2

# Wait for service to be stable
aws ecs wait services-stable \
  --cluster nexus-platform-production-cluster \
  --services nexus-platform-production-service
```

#### 2. Start RDS Instance

```bash
# Start RDS instance
aws rds start-db-instance \
  --db-instance-identifier nexus-platform-production-db

# Wait for instance to be available
aws rds wait db-instance-available \
  --db-instance-identifier nexus-platform-production-db
```

### Stopping Services

#### 1. Stop ECS Service

```bash
# Scale down to 0
aws ecs update-service \
  --cluster nexus-platform-production-cluster \
  --service nexus-platform-production-service \
  --desired-count 0

# Wait for tasks to stop
aws ecs wait services-stable \
  --cluster nexus-platform-production-cluster \
  --services nexus-platform-production-service
```

#### 2. Stop RDS Instance

```bash
# Stop RDS instance
aws rds stop-db-instance \
  --db-instance-identifier nexus-platform-production-db

# Wait for instance to be stopped
aws rds wait db-instance-stopped \
  --db-instance-identifier nexus-platform-production-db
```

### Scaling Operations

#### 1. Scale ECS Service

```bash
# Scale up
aws ecs update-service \
  --cluster nexus-platform-production-cluster \
  --service nexus-platform-production-service \
  --desired-count 5

# Scale down
aws ecs update-service \
  --cluster nexus-platform-production-cluster \
  --service nexus-platform-production-service \
  --desired-count 2
```

#### 2. Scale RDS Instance

```bash
# Modify instance class
aws rds modify-db-instance \
  --db-instance-identifier nexus-platform-production-db \
  --db-instance-class db.t3.small \
  --apply-immediately

# Modify storage
aws rds modify-db-instance \
  --db-instance-identifier nexus-platform-production-db \
  --allocated-storage 100 \
  --apply-immediately
```

## Monitoring and Alerting

### CloudWatch Dashboards

#### 1. Access Dashboard

```bash
# Open dashboard in browser
open "https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#dashboards:name=nexus-platform-production-dashboard"
```

#### 2. Key Metrics to Monitor

- **ECS Metrics**: CPUUtilization, MemoryUtilization
- **ALB Metrics**: TargetResponseTime, RequestCount, HTTPCode_Target_5XX_Count
- **RDS Metrics**: CPUUtilization, DatabaseConnections, FreeStorageSpace
- **Redis Metrics**: CPUUtilization, CurrConnections, CacheHits

### Alert Management

#### 1. Check Active Alarms

```bash
# List all alarms
aws cloudwatch describe-alarms \
  --alarm-names nexus-platform-production-high-cpu \
  nexus-platform-production-high-memory \
  nexus-platform-production-high-response-time \
  nexus-platform-production-high-error-rate
```

#### 2. Acknowledge Alarms

```bash
# Set alarm state
aws cloudwatch set-alarm-state \
  --alarm-name nexus-platform-production-high-cpu \
  --state-value OK \
  --state-reason "Manual acknowledgment"
```

#### 3. Create Custom Alarms

```bash
# Create custom alarm
aws cloudwatch put-metric-alarm \
  --alarm-name nexus-platform-production-custom-alarm \
  --alarm-description "Custom alarm for specific metric" \
  --metric-name CustomMetric \
  --namespace NexusPlatform/Custom \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-west-2:123456789012:nexus-platform-production-alerts
```

### Log Analysis

#### 1. Application Logs

```bash
# Stream logs in real-time
aws logs tail /aws/ecs/nexus-platform-production --follow

# Search for specific patterns
aws logs filter-log-events \
  --log-group-name /aws/ecs/nexus-platform-production \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000

# Search for specific user
aws logs filter-log-events \
  --log-group-name /aws/ecs/nexus-platform-production \
  --filter-pattern "user_id:12345" \
  --start-time $(date -d '1 hour ago' +%s)000
```

#### 2. Database Logs

```bash
# Check RDS logs
aws logs describe-log-streams \
  --log-group-name /aws/rds/instance/nexus-platform-production-db/error

# Download log file
aws logs get-log-events \
  --log-group-name /aws/rds/instance/nexus-platform-production-db/error \
  --log-stream-name error/postgresql.log.2024-01-01-12
```

## Backup and Recovery

### Database Backups

#### 1. Create Manual Backup

```bash
# Create snapshot
aws rds create-db-snapshot \
  --db-instance-identifier nexus-platform-production-db \
  --db-snapshot-identifier nexus-platform-manual-$(date +%Y%m%d-%H%M%S)

# Wait for snapshot to complete
aws rds wait db-snapshot-completed \
  --db-snapshot-identifier nexus-platform-manual-$(date +%Y%m%d-%H%M%S)
```

#### 2. Restore from Backup

```bash
# List available snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier nexus-platform-production-db \
  --query 'DBSnapshots[?Status==`available`]'

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier nexus-platform-restored-db \
  --db-snapshot-identifier nexus-platform-manual-20240101-120000
```

#### 3. Point-in-Time Recovery

```bash
# Restore to specific time
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier nexus-platform-production-db \
  --target-db-instance-identifier nexus-platform-restored-db \
  --restore-time 2024-01-01T12:00:00Z
```

### Application Data Backup

#### 1. Backup to S3

```bash
# Create backup script
cat > backup-application-data.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_BUCKET="nexus-platform-production-backups"

# Backup database
pg_dump -h $RDS_ENDPOINT -U nexus_admin nexus_platform > db_backup_$DATE.sql

# Backup Redis data
redis-cli -h $REDIS_ENDPOINT --rdb redis_backup_$DATE.rdb

# Upload to S3
aws s3 cp db_backup_$DATE.sql s3://$BACKUP_BUCKET/database/
aws s3 cp redis_backup_$DATE.rdb s3://$BACKUP_BUCKET/redis/
EOF

chmod +x backup-application-data.sh
./backup-application-data.sh
```

#### 2. Restore from S3

```bash
# Download from S3
aws s3 cp s3://nexus-platform-production-backups/database/db_backup_20240101-120000.sql ./

# Restore database
psql -h $RDS_ENDPOINT -U nexus_admin nexus_platform < db_backup_20240101-120000.sql
```

### Disaster Recovery

#### 1. Test DR Procedures

```bash
# Trigger DR test
aws lambda invoke \
  --function-name nexus-platform-production-disaster-recovery \
  --payload '{}' \
  response.json

# Check DR test results
cat response.json
```

#### 2. Failover Procedures

```bash
# Update DNS to point to DR region
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890 \
  --change-batch file://failover-change.json
```

## Security Operations

### Access Management

#### 1. Check IAM Users

```bash
# List IAM users
aws iam list-users \
  --query 'Users[].{UserName:UserName,CreateDate:CreateDate,LastUsed:PasswordLastUsed}'

# Check user access keys
aws iam list-access-keys \
  --user-name username
```

#### 2. Rotate Access Keys

```bash
# Create new access key
aws iam create-access-key \
  --user-name username

# Delete old access key
aws iam delete-access-key \
  --user-name username \
  --access-key-id AKIAIOSFODNN7EXAMPLE
```

### Security Groups

#### 1. Review Security Groups

```bash
# List security groups
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=nexus-platform*" \
  --query 'SecurityGroups[].{GroupId:GroupId,GroupName:GroupName,Description:Description}'

# Check security group rules
aws ec2 describe-security-groups \
  --group-ids sg-12345678 \
  --query 'SecurityGroups[0].IpPermissions'
```

#### 2. Update Security Groups

```bash
# Add ingress rule
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Remove ingress rule
aws ec2 revoke-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

### Certificate Management

#### 1. Check SSL Certificates

```bash
# List certificates
aws acm list-certificates \
  --query 'CertificateSummaryList[].{DomainName:DomainName,Status:Status,Expiry:NotAfter}'

# Check certificate details
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012
```

#### 2. Renew Certificates

```bash
# Request new certificate
aws acm request-certificate \
  --domain-name your-domain.com \
  --validation-method DNS \
  --region us-east-1
```

## Performance Optimization

### ECS Optimization

#### 1. Check Resource Utilization

```bash
# Get CPU and memory metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=nexus-platform-production-service Name=ClusterName,Value=nexus-platform-production-cluster \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

#### 2. Optimize Task Definition

```bash
# Get current task definition
aws ecs describe-task-definition \
  --task-definition nexus-platform-production-task \
  --query 'taskDefinition' > current-task-def.json

# Update CPU and memory
# Edit current-task-def.json

# Register new task definition
aws ecs register-task-definition \
  --cli-input-json file://current-task-def.json
```

### Database Optimization

#### 1. Check Database Performance

```bash
# Get RDS metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=nexus-platform-production-db \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

#### 2. Optimize Database

```bash
# Modify instance class
aws rds modify-db-instance \
  --db-instance-identifier nexus-platform-production-db \
  --db-instance-class db.t3.medium \
  --apply-immediately
```

## Incident Response

### Incident Classification

#### 1. Severity Levels

- **P1 - Critical**: Service completely down, data loss
- **P2 - High**: Major functionality affected
- **P3 - Medium**: Minor functionality affected
- **P4 - Low**: Cosmetic issues, workarounds available

#### 2. Response Times

- **P1**: 15 minutes
- **P2**: 1 hour
- **P3**: 4 hours
- **P4**: 24 hours

### Incident Procedures

#### 1. Initial Response

```bash
# Create incident ticket
# Notify stakeholders
# Gather initial information
aws ecs describe-services \
  --cluster nexus-platform-production-cluster \
  --services nexus-platform-production-service
```

#### 2. Investigation

```bash
# Check logs
aws logs tail /aws/ecs/nexus-platform-production --since 1h

# Check metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --end-time $(date +%s)000 \
  --period 300 \
  --statistics Average
```

#### 3. Resolution

```bash
# Implement fix
# Test solution
# Monitor for stability
```

#### 4. Post-Incident

```bash
# Document incident
# Update runbooks
# Schedule post-mortem
```

## Maintenance Procedures

### Regular Maintenance

#### 1. Daily Tasks

- [ ] Check service health
- [ ] Review alerts
- [ ] Monitor resource usage
- [ ] Check backup status

#### 2. Weekly Tasks

- [ ] Review security groups
- [ ] Check certificate expiry
- [ ] Update dependencies
- [ ] Review logs

#### 3. Monthly Tasks

- [ ] Test disaster recovery
- [ ] Review access permissions
- [ ] Update documentation
- [ ] Performance review

### Scheduled Maintenance

#### 1. Application Updates

```bash
# Build new image
docker build -t nexus-platform-backend:v2.0.0 .

# Push to ECR
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/nexus-platform-production-backend:v2.0.0

# Update ECS service
aws ecs update-service \
  --cluster nexus-platform-production-cluster \
  --service nexus-platform-production-service \
  --task-definition nexus-platform-production-task:v2.0.0
```

#### 2. Infrastructure Updates

```bash
# Plan changes
terraform plan -var-file="terraform.tfvars"

# Apply changes
terraform apply -var-file="terraform.tfvars"
```

### Emergency Contacts

#### 1. On-Call Rotation

- **Primary**: +1-555-0123
- **Secondary**: +1-555-0124
- **Manager**: +1-555-0125

#### 2. Escalation Path

1. On-call engineer
2. Team lead
3. Engineering manager
4. CTO

#### 3. Communication Channels

- **Slack**: #nexus-platform-ops
- **Email**: ops@nexus-platform.com
- **PagerDuty**: nexus-platform-alerts

---

**Last Updated**: January 2024
**Version**: 1.0.0
