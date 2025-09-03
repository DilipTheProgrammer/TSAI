# ClinicalBERT FastAPI Service

A production-ready FastAPI service that integrates ClinicalBERT for processing clinical notes and delivering predictive insights, compatible with HL7 FHIR standards.

## Features

- 🏥 **FHIR R4 Compliance**: Full support for HL7 FHIR R4 resources
- 🤖 **ClinicalBERT Integration**: Advanced clinical NLP using Bio_ClinicalBERT
- 🔒 **Enterprise Security**: OAuth 2.0, SMART on FHIR, audit logging
- 📊 **Predictive Analytics**: 30-day readmission prediction and risk assessment
- 🔍 **Clinical Entity Extraction**: Automated extraction of medical entities
- 🔎 **Semantic Search**: Find similar patient cases using embeddings
- 👥 **Cohort Identification**: Identify patient groups based on clinical criteria
- ☁️ **AWS Ready**: Complete deployment automation for AWS EC2

## Quick Start

### Local Development

1. **Clone the repository**
\`\`\`bash
git clone https://github.com/your-org/clinicalbert-api.git
cd clinicalbert-api
\`\`\`

2. **Start with Docker Compose**
\`\`\`bash
# Development environment
make dev

# Production environment
make prod
\`\`\`

3. **Access the API**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Metrics: http://localhost:9090

### AWS Deployment

1. **Prerequisites**
\`\`\`bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Create EC2 key pair
aws ec2 create-key-pair --key-name clinicalbert-key --query 'KeyMaterial' --output text > clinicalbert-key.pem
chmod 400 clinicalbert-key.pem
\`\`\`

2. **Deploy to AWS**
\`\`\`bash
# Deploy infrastructure
./scripts/deploy.sh production us-east-1

# Set up monitoring
./scripts/monitoring.sh production us-east-1
\`\`\`

3. **Access your deployment**
\`\`\`bash
# Get load balancer URL
aws cloudformation describe-stacks \
    --stack-name clinicalbert-production \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text
\`\`\`

## API Endpoints

### Core Endpoints

- `POST /api/v1/predict_readmission` - 30-day readmission prediction
- `POST /api/v1/risk_trajectory` - Dynamic risk assessment during hospital stay
- `POST /api/v1/extract_entities` - Clinical entity extraction from text
- `POST /api/v1/search_cases` - Semantic search for similar patient cases
- `POST /api/v1/cohort_identification` - Identify patient cohorts

### System Endpoints

- `GET /health` - Health check endpoint
- `GET /metrics` - Prometheus metrics
- `GET /docs` - Interactive API documentation
- `POST /api/v1/auth/token` - OAuth 2.0 token endpoint

## Architecture

\`\`\`
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│   FastAPI App   │────│   PostgreSQL    │
│      (ALB)      │    │   (Auto Scaling)│    │     (RDS)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Redis Cache   │    │  ClinicalBERT   │
                       │  (ElastiCache)  │    │     Model       │
                       └─────────────────┘    └─────────────────┘
\`\`\`

## Security & Compliance

- **Authentication**: OAuth 2.0 / SMART on FHIR
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: TLS 1.3 for data in transit, AES-256 for data at rest
- **Audit Logging**: Comprehensive audit trails for HIPAA compliance
- **PHI Protection**: Automatic anonymization and de-identification
- **GDPR Compliance**: Data retention policies and right to erasure

## Monitoring & Observability

- **Health Checks**: Automated health monitoring with auto-recovery
- **Metrics**: Prometheus metrics with Grafana dashboards
- **Logging**: Structured JSON logging with CloudWatch integration
- **Alerting**: CloudWatch alarms for critical system events
- **Tracing**: Distributed tracing for request flow analysis

## Development

### Running Tests
\`\`\`bash
make test
\`\`\`

### Code Quality
\`\`\`bash
make lint
make format
\`\`\`

### Database Migrations
\`\`\`bash
make migrate
\`\`\`

## Production Considerations

### Scaling
- Auto Scaling Groups handle traffic spikes automatically
- Redis caching reduces database load
- Model inference is optimized for batch processing

### Backup & Recovery
- Automated daily database backups to S3
- Point-in-time recovery capability
- Cross-region backup replication for disaster recovery

### Performance
- Model caching reduces inference latency
- Connection pooling optimizes database performance
- CDN integration for static assets

## Support

For issues and support:
1. Check the [troubleshooting guide](docs/troubleshooting.md)
2. Review [API documentation](www.google.com)
3. Contact support at support@your-org.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
