#!/bin/bash
set -e

PROJECT_ID="mcp-experiment-476223"
REGION="us-central1"
PRODUCT="${1:-weaviate}"

if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh <product>"
    echo "Available products: weaviate, etc."
    exit 1
fi

SERVICE_NAME="${PRODUCT}-docs-mcp"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/mcp-servers/${SERVICE_NAME}:latest"

echo "Building Docker image for ${PRODUCT}..."
docker build --platform linux/amd64 -t ${IMAGE} .

echo "Pushing to Artifact Registry..."
docker push ${IMAGE}

echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars PRODUCT=${PRODUCT} \
    --set-env-vars MCP_TRANSPORT=streamable-http \
    --set-env-vars WCD_URL="$(grep WCD_URL .env.production | cut -d '=' -f2)" \
    --set-env-vars WCD_KEY="$(grep WCD_KEY .env.production | cut -d '=' -f2)" \
    --set-env-vars COHERE_API_KEY="$(grep COHERE_API_KEY .env.production | cut -d '=' -f2)" \
    --set-env-vars ANTHROPIC_API_KEY="$(grep ANTHROPIC_API_KEY .env.production | cut -d '=' -f2)" \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0

echo "Deployment complete!"
gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)'
