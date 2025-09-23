#!/bin/bash

# Deployment script for ImpactAnalyzer microservices
set -e

PROJECT_ID=${1:-"impact-analyzer-project"}
REGION=${2:-"us-central1"}

echo "🚀 Deploying ImpactAnalyzer microservices to Google Cloud"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Set project
gcloud config set project $PROJECT_ID

# Build and deploy using Cloud Build
echo "🏗️ Building and deploying microservices..."
gcloud builds submit --config=cloudbuild.yaml \
    --substitutions=_REGION=$REGION \
    --timeout=1200s

echo "⏰ Setting up Cloud Scheduler for daily refresh..."
gcloud scheduler jobs create http daily-dependency-refresh \
    --schedule="0 2 * * *" \
    --uri="https://ms-index-uc.a.run.app/index/daily-refresh" \
    --http-method=POST \
    --headers="Content-Type=application/json,X-Impact-Analyzer-Api-Key=dev-key-123" \
    --location=$REGION || true

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Service URLs:"
echo "MS-Index: https://ms-index-uc.a.run.app"
echo "MS-MR: https://ms-mr-uc.a.run.app"
echo "MS-Common: https://ms-common-uc.a.run.app"
echo "MS-AI: https://ms-ai-uc.a.run.app"
echo "MS-TestCase: https://ms-testcase-uc.a.run.app"
echo ""
echo "📋 Next steps:"
echo "1. Update your frontend environment variables with the service URLs above"
echo "2. Test the services using the provided test scripts"
echo "3. Configure the IntelliJ plugin with the MS-Index and MS-MR URLs"