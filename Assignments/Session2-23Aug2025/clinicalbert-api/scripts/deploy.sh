#!/bin/bash

set -e

# ClinicalBERT API Deployment Script for AWS EC2
# Usage: ./deploy.sh [environment] [region]

ENVIRONMENT=${1:-production}
REGION=${2:-us-east-1}
STACK_NAME="clinicalbert-${ENVIRONMENT}"

echo "🚀 Deploying ClinicalBERT API to AWS"
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "Stack: ${STACK_NAME}"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure'"
    exit 1
fi

# Create secrets for database password
echo "🔐 Creating database password secret..."
DB_PASSWORD=$(openssl rand -base64 32)
aws secretsmanager create-secret \
    --name "${ENVIRONMENT}-db-password" \
    --description "Database password for ClinicalBERT ${ENVIRONMENT}" \
    --secret-string "{\"password\":\"${DB_PASSWORD}\"}" \
    --region ${REGION} || \
aws secretsmanager update-secret \
    --secret-id "${ENVIRONMENT}-db-password" \
    --secret-string "{\"password\":\"${DB_PASSWORD}\"}" \
    --region ${REGION}

# Deploy CloudFormation stack
echo "☁️ Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file aws/cloudformation/infrastructure.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        Environment=${ENVIRONMENT} \
        KeyPairName=${KEY_PAIR_NAME:-clinicalbert-key} \
    --capabilities CAPABILITY_IAM \
    --region ${REGION} \
    --tags \
        Project=ClinicalBERT \
        Environment=${ENVIRONMENT}

# Get stack outputs
echo "📋 Getting stack outputs..."
ALB_DNS=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text)

DB_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
    --output text)

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Application URL: http://${ALB_DNS}"
echo "🗄️ Database Endpoint: ${DB_ENDPOINT}"
echo ""
echo "📝 Next steps:"
echo "1. Update your DNS to point to: ${ALB_DNS}"
echo "2. Configure SSL certificate for HTTPS"
echo "3. Set up monitoring and alerting"
echo "4. Run database migrations"
