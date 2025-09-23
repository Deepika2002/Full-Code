#!/bin/bash

# Setup script for Google Cloud Platform deployment
# This script sets up the necessary GCP resources for ImpactAnalyzer

set -e

# Configuration
PROJECT_ID=${1:-"impact-analyzer-project"}
REGION=${2:-"us-central1"}
ZONE=${3:-"us-central1-a"}

echo "🚀 Setting up ImpactAnalyzer on Google Cloud Platform"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Zone: $ZONE"

# Set project
echo "📋 Setting up project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sql.googleapis.com \
    storage.googleapis.com \
    aiplatform.googleapis.com \
    cloudscheduler.googleapis.com \
    secretmanager.googleapis.com \
    container.googleapis.com

# Create service account
echo "👤 Creating service account..."
gcloud iam service-accounts create impact-analyzer-services \
    --display-name="ImpactAnalyzer Microservices" \
    --description="Service account for ImpactAnalyzer microservices" || true

# Grant necessary roles
echo "🔐 Granting IAM roles..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:impact-analyzer-services@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:impact-analyzer-services@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:impact-analyzer-services@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create Cloud SQL instances
echo "🗄️ Creating Cloud SQL instances..."
gcloud sql instances create impact-analyzer-db \
    --database-version=MYSQL_8_0 \
    --tier=db-f1-micro \
    --region=$REGION \
    --backup-start-time=02:00 \
    --enable-bin-log \
    --authorized-networks=0.0.0.0/0 || true

gcloud sql instances create impact-analyzer-vector-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=$REGION \
    --backup-start-time=03:00 \
    --authorized-networks=0.0.0.0/0 || true

# Create databases
echo "📊 Creating databases..."
gcloud sql databases create impact_analyzer --instance=impact-analyzer-db || true
gcloud sql databases create vectors --instance=impact-analyzer-vector-db || true

# Create database users
echo "👥 Creating database users..."
gcloud sql users create impact_user \
    --instance=impact-analyzer-db \
    --password=impact_password_123 || true

gcloud sql users create vector_user \
    --instance=impact-analyzer-vector-db \
    --password=vector_password_123 || true

# Create Cloud Storage buckets
echo "🪣 Creating Cloud Storage buckets..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-impact-analyzer-storage || true
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-impact-analyzer-vectors || true
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-impact-analyzer-logs || true

# Set bucket permissions
echo "🔒 Setting bucket permissions..."
gsutil iam ch serviceAccount:impact-analyzer-services@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$PROJECT_ID-impact-analyzer-storage
gsutil iam ch serviceAccount:impact-analyzer-services@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$PROJECT_ID-impact-analyzer-vectors
gsutil iam ch serviceAccount:impact-analyzer-services@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$PROJECT_ID-impact-analyzer-logs

# Create secrets
echo "🔑 Creating secrets..."
echo -n "your-openai-api-key-here" | gcloud secrets create openai-api-key --data-file=- || true
echo -n "dev-key-123" | gcloud secrets create impact-analyzer-api-key --data-file=- || true

# Grant secret access
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:impact-analyzer-services@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding impact-analyzer-api-key \
    --member="serviceAccount:impact-analyzer-services@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Get connection details
echo "📋 Getting connection details..."
DB_CONNECTION_NAME=$(gcloud sql instances describe impact-analyzer-db --format="value(connectionName)")
VECTOR_DB_CONNECTION_NAME=$(gcloud sql instances describe impact-analyzer-vector-db --format="value(connectionName)")
DB_IP=$(gcloud sql instances describe impact-analyzer-db --format="value(ipAddresses[0].ipAddress)")
VECTOR_DB_IP=$(gcloud sql instances describe impact-analyzer-vector-db --format="value(ipAddresses[0].ipAddress)")

echo "✅ Setup completed successfully!"
echo ""
echo "📋 Connection Details:"
echo "Main Database Connection Name: $DB_CONNECTION_NAME"
echo "Vector Database Connection Name: $VECTOR_DB_CONNECTION_NAME"
echo "Main Database IP: $DB_IP"
echo "Vector Database IP: $VECTOR_DB_IP"
echo ""
echo "🪣 Storage Buckets:"
echo "Main Storage: gs://$PROJECT_ID-impact-analyzer-storage"
echo "Vector Storage: gs://$PROJECT_ID-impact-analyzer-vectors"
echo "Logs Storage: gs://$PROJECT_ID-impact-analyzer-logs"
echo ""
echo "🔑 Service Account: impact-analyzer-services@$PROJECT_ID.iam.gserviceaccount.com"
echo ""
echo "Next steps:"
echo "1. Update your .env files with the connection details above"
echo "2. Update the OpenAI API key secret: gcloud secrets versions add openai-api-key --data-file=<your-key-file>"
echo "3. Build and deploy the microservices using Cloud Build"
echo "4. Set up the frontend with the Cloud Run URLs"