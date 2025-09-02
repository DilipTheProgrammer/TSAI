#!/bin/bash

# EC2 Instance Setup Script for ClinicalBERT API
# This script is run on each EC2 instance during launch

set -e

LOG_FILE="/var/log/clinicalbert-setup.log"
exec > >(tee -a ${LOG_FILE})
exec 2>&1

echo "🚀 Starting ClinicalBERT API setup on EC2 instance"
echo "Timestamp: $(date)"

# Update system
echo "📦 Updating system packages..."
yum update -y

# Install required packages
echo "📦 Installing Docker and dependencies..."
yum install -y docker git htop curl wget unzip

# Start Docker service
echo "🐳 Starting Docker service..."
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Install AWS CLI v2
echo "☁️ Installing AWS CLI v2..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

# Install CloudWatch agent
echo "📊 Installing CloudWatch agent..."
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm
rm amazon-cloudwatch-agent.rpm

# Create application directory
echo "📁 Setting up application directory..."
mkdir -p /opt/clinicalbert
cd /opt/clinicalbert

# Clone application repository (replace with your actual repo)
echo "📥 Cloning application repository..."
git clone https://github.com/your-org/clinicalbert-api.git .

# Get instance metadata
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)

# Get secrets from AWS Secrets Manager
echo "🔐 Retrieving secrets..."
DB_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id "${ENVIRONMENT:-production}-db-password" \
    --region ${REGION} \
    --query SecretString --output text | jq -r .password)

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
# Environment Configuration
ENVIRONMENT=${ENVIRONMENT:-production}
INSTANCE_ID=${INSTANCE_ID}
REGION=${REGION}

# Database Configuration
DATABASE_URL=postgresql://clinicalbert:${DB_PASSWORD}@${DATABASE_HOST}:5432/clinicalbert
REDIS_URL=redis://${REDIS_HOST}:6379

# Security Configuration
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=ClinicalBERT API
VERSION=1.0.0

# Model Configuration
MODEL_CACHE_DIR=/opt/models
HUGGINGFACE_CACHE_DIR=/opt/huggingface

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Health Check Configuration
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=20

# CORS Configuration
ALLOWED_ORIGINS=*
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
EOF

# Create model cache directory
echo "🤖 Setting up model cache directory..."
mkdir -p /opt/models /opt/huggingface
chown -R ec2-user:ec2-user /opt/models /opt/huggingface

# Download and cache ClinicalBERT model
echo "📥 Pre-downloading ClinicalBERT model..."
su - ec2-user -c "cd /opt/clinicalbert && python3 -c '
import os
os.environ[\"TRANSFORMERS_CACHE\"] = \"/opt/huggingface\"
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained(\"emilyalsentzer/Bio_ClinicalBERT\")
model = AutoModel.from_pretrained(\"emilyalsentzer/Bio_ClinicalBERT\")
print(\"Model cached successfully\")
'"

# Set up log rotation
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/clinicalbert << EOF
/opt/clinicalbert/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ec2-user ec2-user
    postrotate
        docker-compose -f /opt/clinicalbert/docker-compose.prod.yml restart app
    endscript
}
EOF

# Create systemd service
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/clinicalbert.service << EOF
[Unit]
Description=ClinicalBERT API Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/clinicalbert
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0
User=ec2-user
Group=ec2-user

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable clinicalbert.service

# Start the application
echo "🚀 Starting ClinicalBERT API..."
cd /opt/clinicalbert
chown -R ec2-user:ec2-user /opt/clinicalbert
su - ec2-user -c "cd /opt/clinicalbert && docker-compose -f docker-compose.prod.yml up -d"

# Wait for application to be ready
echo "⏳ Waiting for application to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Application is ready!"
        break
    fi
    echo "Waiting... (${i}/30)"
    sleep 10
done

# Setup CloudWatch monitoring
echo "📊 Setting up CloudWatch monitoring..."
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << EOF
{
    "metrics": {
        "namespace": "ClinicalBERT/${ENVIRONMENT:-production}",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_iowait", "cpu_usage_user", "cpu_usage_system"],
                "metrics_collection_interval": 60
            },
            "disk": {
                "measurement": ["used_percent"],
                "metrics_collection_interval": 60,
                "resources": ["*"]
            },
            "mem": {
                "measurement": ["mem_used_percent"],
                "metrics_collection_interval": 60
            }
        }
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/opt/clinicalbert/logs/app.log",
                        "log_group_name": "/aws/ec2/clinicalbert/${ENVIRONMENT:-production}",
                        "log_stream_name": "{instance_id}/app.log"
                    },
                    {
                        "file_path": "/var/log/clinicalbert-setup.log",
                        "log_group_name": "/aws/ec2/clinicalbert/${ENVIRONMENT:-production}",
                        "log_stream_name": "{instance_id}/setup.log"
                    }
                ]
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
    -s

echo "✅ ClinicalBERT API setup completed successfully!"
echo "🌐 Application is running on http://localhost:8000"
echo "📊 Health check: http://localhost:8000/health"
echo "📚 API docs: http://localhost:8000/docs"
