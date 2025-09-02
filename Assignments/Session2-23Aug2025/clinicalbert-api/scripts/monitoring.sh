#!/bin/bash

# Monitoring and Health Check Script for ClinicalBERT API

set -e

ENVIRONMENT=${1:-production}
REGION=${2:-us-east-1}

echo "📊 Setting up monitoring for ClinicalBERT API"

# Create CloudWatch Log Groups
aws logs create-log-group \
    --log-group-name "/aws/ec2/clinicalbert/${ENVIRONMENT}" \
    --region ${REGION} || true

aws logs create-log-group \
    --log-group-name "/aws/lambda/clinicalbert-health-check" \
    --region ${REGION} || true

# Create CloudWatch Alarms
echo "🚨 Creating CloudWatch alarms..."

# High CPU utilization alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "ClinicalBERT-${ENVIRONMENT}-HighCPU" \
    --alarm-description "High CPU utilization for ClinicalBERT instances" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions "arn:aws:sns:${REGION}:$(aws sts get-caller-identity --query Account --output text):clinicalbert-alerts" \
    --dimensions Name=AutoScalingGroupName,Value="clinicalbert-${ENVIRONMENT}-asg" \
    --region ${REGION}

# High memory utilization alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "ClinicalBERT-${ENVIRONMENT}-HighMemory" \
    --alarm-description "High memory utilization for ClinicalBERT instances" \
    --metric-name MemoryUtilization \
    --namespace CWAgent \
    --statistic Average \
    --period 300 \
    --threshold 85 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions "arn:aws:sns:${REGION}:$(aws sts get-caller-identity --query Account --output text):clinicalbert-alerts" \
    --dimensions Name=AutoScalingGroupName,Value="clinicalbert-${ENVIRONMENT}-asg" \
    --region ${REGION}

# Application health check alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "ClinicalBERT-${ENVIRONMENT}-HealthCheck" \
    --alarm-description "ClinicalBERT application health check failure" \
    --metric-name HealthCheck \
    --namespace ClinicalBERT/${ENVIRONMENT} \
    --statistic Average \
    --period 60 \
    --threshold 1 \
    --comparison-operator LessThanThreshold \
    --evaluation-periods 3 \
    --alarm-actions "arn:aws:sns:${REGION}:$(aws sts get-caller-identity --query Account --output text):clinicalbert-alerts" \
    --region ${REGION}

echo "✅ Monitoring setup completed!"
