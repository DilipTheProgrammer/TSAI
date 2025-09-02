#!/bin/bash

# Backup Script for ClinicalBERT API

set -e

ENVIRONMENT=${1:-production}
REGION=${2:-us-east-1}
BACKUP_BUCKET="clinicalbert-backups-$(aws sts get-caller-identity --query Account --output text)"

echo "💾 Starting backup process for ClinicalBERT ${ENVIRONMENT}"

# Create backup bucket if it doesn't exist
aws s3 mb s3://${BACKUP_BUCKET} --region ${REGION} || true

# Enable versioning on backup bucket
aws s3api put-bucket-versioning \
    --bucket ${BACKUP_BUCKET} \
    --versioning-configuration Status=Enabled

# Get database endpoint
DB_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "clinicalbert-${ENVIRONMENT}" \
    --region ${REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
    --output text)

# Get database password
DB_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id "${ENVIRONMENT}-db-password" \
    --region ${REGION} \
    --query SecretString --output text | jq -r .password)

# Create database backup
echo "🗄️ Creating database backup..."
BACKUP_FILE="clinicalbert-db-backup-$(date +%Y%m%d-%H%M%S).sql"

PGPASSWORD=${DB_PASSWORD} pg_dump \
    -h ${DB_ENDPOINT} \
    -U clinicalbert \
    -d clinicalbert \
    --no-password \
    --verbose \
    --clean \
    --if-exists \
    --create > ${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_FILE}
BACKUP_FILE="${BACKUP_FILE}.gz"

# Upload to S3
echo "☁️ Uploading backup to S3..."
aws s3 cp ${BACKUP_FILE} s3://${BACKUP_BUCKET}/database/${BACKUP_FILE} \
    --storage-class STANDARD_IA \
    --server-side-encryption AES256

# Clean up local backup file
rm ${BACKUP_FILE}

# Backup application logs
echo "📝 Backing up application logs..."
LOG_BACKUP="clinicalbert-logs-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf ${LOG_BACKUP} /opt/clinicalbert/logs/ || true

aws s3 cp ${LOG_BACKUP} s3://${BACKUP_BUCKET}/logs/${LOG_BACKUP} \
    --storage-class STANDARD_IA \
    --server-side-encryption AES256

rm ${LOG_BACKUP}

# Clean up old backups (keep last 30 days)
echo "🧹 Cleaning up old backups..."
aws s3 ls s3://${BACKUP_BUCKET}/database/ | \
    awk '{print $4}' | \
    head -n -30 | \
    xargs -I {} aws s3 rm s3://${BACKUP_BUCKET}/database/{}

aws s3 ls s3://${BACKUP_BUCKET}/logs/ | \
    awk '{print $4}' | \
    head -n -30 | \
    xargs -I {} aws s3 rm s3://${BACKUP_BUCKET}/logs/{}

echo "✅ Backup completed successfully!"
echo "📍 Database backup: s3://${BACKUP_BUCKET}/database/${BACKUP_FILE}"
echo "📍 Logs backup: s3://${BACKUP_BUCKET}/logs/${LOG_BACKUP}"
