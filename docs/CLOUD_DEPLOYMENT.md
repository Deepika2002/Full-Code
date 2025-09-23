# Cloud Deployment Guide

This guide walks you through deploying the ImpactAnalyzer system to Google Cloud Platform.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed and configured
3. **Docker** installed (for local testing)
4. **Terraform** installed (optional, for infrastructure as code)

## Quick Start

### 1. Setup Google Cloud Project

```bash
# Create a new project (or use existing)
gcloud projects create impact-analyzer-project --name="ImpactAnalyzer"

# Set the project
gcloud config set project impact-analyzer-project

# Enable billing (required for Cloud SQL, Cloud Run, etc.)
# Do this through the Google Cloud Console
```

### 2. Run Setup Script

```bash
cd backend/deployment
chmod +x setup_gcp.sh
./setup_gcp.sh impact-analyzer-project us-central1
```

This script will:
- Enable required APIs
- Create Cloud SQL instances (MySQL and PostgreSQL)
- Create Cloud Storage buckets
- Set up service accounts and IAM roles
- Create Secret Manager secrets

### 3. Update Configuration

Update the environment files with the connection details provided by the setup script:

```bash
# Copy the template
cp backend/cloud_env_template.env backend/.env

# Update with your actual values
nano backend/.env
```

### 4. Deploy Microservices

```bash
cd backend/deployment
chmod +x deploy.sh
./deploy.sh impact-analyzer-project us-central1
```

This will:
- Build Docker images for all microservices
- Deploy to Cloud Run
- Set up Cloud Scheduler for daily refresh

### 5. Update Frontend Configuration

```bash
# Copy production environment
cp .env.production .env

# Update with your Cloud Run URLs
nano .env
```

## Detailed Setup

### Infrastructure Components

#### 1. Cloud SQL Instances

**Main Database (MySQL 8.0)**
- Instance: `impact-analyzer-db`
- Database: `impact_analyzer`
- User: `impact_user`
- Tier: `db-f1-micro` (can be upgraded for production)

**Vector Database (PostgreSQL 14)**
- Instance: `impact-analyzer-vector-db`
- Database: `vectors`
- User: `vector_user`
- Tier: `db-f1-micro`

#### 2. Cloud Storage Buckets

- **Main Storage**: `{project-id}-impact-analyzer-storage`
- **Vector Storage**: `{project-id}-impact-analyzer-vectors`
- **Logs Storage**: `{project-id}-impact-analyzer-logs`

#### 3. Cloud Run Services

- **MS-Index**: Dependency graph indexing (Port 8001)
- **MS-MR**: Merge request analysis (Port 8002)
- **MS-Common**: Frontend API gateway (Port 8003)
- **MS-AI**: AI analysis service (Port 8004)
- **MS-TestCase**: Test execution service (Port 8005)

#### 4. Additional Services

- **Vertex AI**: Text embeddings and AI analysis
- **Secret Manager**: API keys and sensitive configuration
- **Cloud Scheduler**: Daily refresh jobs
- **Cloud Build**: CI/CD pipeline

### Manual Deployment Steps

If you prefer manual deployment:

#### 1. Create Cloud SQL Instances

```bash
# Main database
gcloud sql instances create impact-analyzer-db \
    --database-version=MYSQL_8_0 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --backup-start-time=02:00 \
    --enable-bin-log

# Vector database
gcloud sql instances create impact-analyzer-vector-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --backup-start-time=03:00
```

#### 2. Create Databases and Users

```bash
# Create databases
gcloud sql databases create impact_analyzer --instance=impact-analyzer-db
gcloud sql databases create vectors --instance=impact-analyzer-vector-db

# Create users
gcloud sql users create impact_user \
    --instance=impact-analyzer-db \
    --password=your_secure_password

gcloud sql users create vector_user \
    --instance=impact-analyzer-vector-db \
    --password=your_secure_password
```

#### 3. Create Storage Buckets

```bash
gsutil mb -p impact-analyzer-project -c STANDARD -l us-central1 gs://impact-analyzer-project-storage
gsutil mb -p impact-analyzer-project -c STANDARD -l us-central1 gs://impact-analyzer-project-vectors
gsutil mb -p impact-analyzer-project -c STANDARD -l us-central1 gs://impact-analyzer-project-logs
```

#### 4. Build and Deploy Services

```bash
# Build all services
gcloud builds submit --config=backend/deployment/cloudbuild.yaml

# Or build individual services
cd backend/ms_index
gcloud builds submit --tag gcr.io/impact-analyzer-project/ms-index

# Deploy to Cloud Run
gcloud run deploy ms-index \
    --image gcr.io/impact-analyzer-project/ms-index \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated
```

## Configuration

### Environment Variables

Each microservice needs these environment variables:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=impact-analyzer-project
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Database
DATABASE_URL=mysql+pymysql://user:pass@ip:3306/impact_analyzer
VECTOR_DB_URL=postgresql://user:pass@ip:5432/vectors

# Storage
GCS_BUCKET_NAME=impact-analyzer-project-storage
GCS_VECTOR_BUCKET=impact-analyzer-project-vectors
GCS_LOGS_BUCKET=impact-analyzer-project-logs

# Vertex AI
VERTEX_AI_PROJECT=impact-analyzer-project
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=textembedding-gecko@003
```

### Secret Manager

Store sensitive data in Secret Manager:

```bash
# OpenAI API Key
echo -n "your-openai-api-key" | gcloud secrets create openai-api-key --data-file=-

# Impact Analyzer API Key
echo -n "your-api-key" | gcloud secrets create impact-analyzer-api-key --data-file=-
```

Access secrets in your application:

```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
response = client.access_secret_version(request={"name": name})
secret_value = response.payload.data.decode("UTF-8")
```

## Monitoring and Logging

### Cloud Logging

All microservices automatically send logs to Cloud Logging. View logs:

```bash
# View logs for a specific service
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=ms-index"

# Follow logs in real-time
gcloud logs tail "resource.type=cloud_run_revision"
```

### Cloud Monitoring

Set up monitoring and alerting:

1. Go to Cloud Monitoring in the console
2. Create alerting policies for:
   - High error rates
   - High latency
   - Resource utilization
   - Database connection issues

### Health Checks

Each service has a health check endpoint:

```bash
curl https://ms-index-uc.a.run.app/index/health
curl https://ms-mr-uc.a.run.app/mr/health
curl https://ms-common-uc.a.run.app/common/health
curl https://ms-ai-uc.a.run.app/ai/health
curl https://ms-testcase-uc.a.run.app/testcase/health
```

## Scaling and Performance

### Cloud Run Scaling

Configure scaling for each service:

```bash
gcloud run services update ms-index \
    --min-instances=1 \
    --max-instances=10 \
    --concurrency=100 \
    --cpu=2 \
    --memory=2Gi
```

### Database Scaling

Upgrade database tiers as needed:

```bash
gcloud sql instances patch impact-analyzer-db \
    --tier=db-n1-standard-2
```

### Storage Optimization

- Use lifecycle policies for automatic cleanup
- Enable compression for logs
- Use regional storage for better performance

## Security

### Network Security

- Cloud SQL instances use private IPs where possible
- Cloud Run services use IAM authentication
- Storage buckets have uniform bucket-level access

### IAM Roles

Principle of least privilege:

```bash
# Service account for microservices
gcloud iam service-accounts create impact-analyzer-services

# Grant minimal required roles
gcloud projects add-iam-policy-binding impact-analyzer-project \
    --member="serviceAccount:impact-analyzer-services@impact-analyzer-project.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"
```

### Data Encryption

- All data encrypted at rest (automatic)
- All data encrypted in transit (HTTPS/TLS)
- Use Secret Manager for sensitive configuration

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check if Cloud SQL Auth proxy is needed
   gcloud sql instances describe impact-analyzer-db
   
   # Test connection
   gcloud sql connect impact-analyzer-db --user=impact_user
   ```

2. **Service Deployment Failures**
   ```bash
   # Check build logs
   gcloud builds log <BUILD_ID>
   
   # Check service logs
   gcloud logs read "resource.type=cloud_run_revision"
   ```

3. **Permission Errors**
   ```bash
   # Check IAM roles
   gcloud projects get-iam-policy impact-analyzer-project
   
   # Test service account permissions
   gcloud auth activate-service-account --key-file=service-account.json
   ```

### Performance Issues

1. **Slow Database Queries**
   - Enable Cloud SQL Insights
   - Add database indexes
   - Upgrade database tier

2. **High Latency**
   - Check Cloud Run cold starts
   - Increase min-instances
   - Optimize code and dependencies

3. **Memory Issues**
   - Increase Cloud Run memory allocation
   - Optimize vector storage and retrieval
   - Use streaming for large datasets

## Cost Optimization

### Resource Management

1. **Use appropriate tiers**
   - Start with `db-f1-micro` for databases
   - Use `1 CPU, 1Gi memory` for Cloud Run services
   - Scale up based on actual usage

2. **Storage lifecycle**
   - Set up automatic deletion for old logs
   - Use nearline/coldline storage for archives
   - Compress large files

3. **Monitoring costs**
   - Set up billing alerts
   - Use Cloud Monitoring to track resource usage
   - Regular cost analysis and optimization

### Free Tier Usage

Google Cloud offers free tier for:
- Cloud Run: 2 million requests/month
- Cloud SQL: db-f1-micro instance
- Cloud Storage: 5GB/month
- Vertex AI: Limited free usage

## Backup and Disaster Recovery

### Database Backups

```bash
# Enable automated backups (done in setup)
gcloud sql instances patch impact-analyzer-db \
    --backup-start-time=02:00 \
    --enable-bin-log

# Manual backup
gcloud sql backups create --instance=impact-analyzer-db
```

### Storage Backups

```bash
# Enable versioning (done in setup)
gsutil versioning set on gs://impact-analyzer-project-storage

# Cross-region replication
gsutil cp -r gs://impact-analyzer-project-storage gs://backup-bucket
```

### Disaster Recovery Plan

1. **Database Recovery**
   - Automated daily backups
   - Point-in-time recovery available
   - Cross-region replica for critical data

2. **Service Recovery**
   - Container images stored in Container Registry
   - Infrastructure as Code with Terraform
   - Automated deployment scripts

3. **Data Recovery**
   - Versioned storage buckets
   - Regular backup verification
   - Recovery testing procedures

## Next Steps

After successful deployment:

1. **Configure IntelliJ Plugin**
   - Update plugin with Cloud Run URLs
   - Test dependency graph extraction
   - Test git diff analysis

2. **Set up Monitoring**
   - Create dashboards
   - Set up alerting
   - Monitor costs

3. **Performance Testing**
   - Load test the APIs
   - Optimize database queries
   - Tune Cloud Run settings

4. **Security Review**
   - Audit IAM permissions
   - Review network security
   - Update secrets rotation

5. **Documentation**
   - Update API documentation
   - Create runbooks
   - Train team members