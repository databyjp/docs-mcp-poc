# Deploying MCP Server to Google Cloud Run

This guide walks you through deploying your documentation MCP server to Google Cloud Run, making it accessible remotely via HTTPS.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and configured ([installation guide](https://cloud.google.com/sdk/docs/install))
3. **Docker** installed locally (for building containers)
4. **Environment variables** from `.env` file

## Architecture Overview

- **Local Mode**: Server runs with `stdio` transport for local Claude Desktop integration
- **Cloud Run Mode**: Server runs with `streamable-http` transport on port 8080, accessible via HTTPS
- **Product-Specific**: Each product (weaviate, togetherai, etc.) requires its own Cloud Run service instance

## Setup Instructions

### 1. Initialize Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create YOUR-PROJECT-ID --name="MCP Documentation Server"

# Set the project as default
gcloud config set project YOUR-PROJECT-ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 2. Configure Docker Registry

Create an Artifact Registry repository for Docker images:

```bash
# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create mcp-servers \
    --repository-format=docker \
    --location=us-central1 \
    --description="MCP documentation servers"

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 3. Prepare Environment Variables

Cloud Run services need your credentials as environment variables. Create a `.env.production` file:

```bash
# Copy your local .env as a template
cp .env .env.production

# Edit .env.production with production values
# Ensure these are set:
# - WCD_URL=your-weaviate-cloud-url
# - WCD_KEY=your-weaviate-api-key
# - COHERE_API_KEY=your-cohere-key
# - ANTHROPIC_API_KEY=your-anthropic-key (if needed)
```

**Security Note**: Never commit `.env.production` to version control. Add it to `.gitignore`.

### 4. Build and Deploy a Service

Deploy a product-specific MCP server (e.g., for Weaviate documentation):

```bash
# Set variables
PROJECT_ID="YOUR-PROJECT-ID"
REGION="us-central1"
PRODUCT="weaviate"  # or "togetherai", etc.
SERVICE_NAME="${PRODUCT}-docs-mcp"

# Build the container image
docker build \
    --platform linux/amd64 \
    -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/mcp-servers/${SERVICE_NAME}:latest \
    .

# Push to Artifact Registry
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/mcp-servers/${SERVICE_NAME}:latest

# Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/mcp-servers/${SERVICE_NAME}:latest \
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
```

After deployment, you'll receive a service URL like:
```
https://weaviate-docs-mcp-XXXXX-uc.a.run.app
```

### 5. Deploy Additional Products

To serve multiple products (e.g., togetherai), repeat the build/deploy with a different `PRODUCT` value:

```bash
PRODUCT="togetherai"
SERVICE_NAME="${PRODUCT}-docs-mcp"

# Build, push, and deploy using the same commands as above
docker build --platform linux/amd64 -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/mcp-servers/${SERVICE_NAME}:latest .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/mcp-servers/${SERVICE_NAME}:latest
gcloud run deploy ${SERVICE_NAME} \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/mcp-servers/${SERVICE_NAME}:latest \
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
```

### 6. Configure Claude Desktop Client

Update your Claude Desktop configuration to use the remote MCP server:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "weaviate-docs": {
      "url": "https://weaviate-docs-mcp-XXXXX-uc.a.run.app/mcp",
      "transport": "http"
    },
    "togetherai-docs": {
      "url": "https://togetherai-docs-mcp-XXXXX-uc.a.run.app/mcp",
      "transport": "http"
    }
  }
}
```

**Important**:
- Use the `/mcp` endpoint (FastMCP's default for streamable-http)
- Use `http` as the transport type (for MCP's Streamable HTTP protocol)
- Replace `XXXXX` with your actual Cloud Run service URLs

Restart Claude Desktop to apply the configuration.

### 6b. Configure Claude Code CLI

For Claude Code, use the `claude mcp add` command:

```bash
# Get your service URL
SERVICE_URL=$(gcloud run services describe weaviate-docs-mcp --region us-central1 --format 'value(status.url)')

# Add the MCP server with HTTP transport
claude mcp add --transport http weaviate-docs "${SERVICE_URL}/mcp"

# Verify the connection
claude mcp list
```

**Note**: Use `--transport http` (not `sse`) because FastMCP's `streamable-http` transport implements the MCP Streamable HTTP protocol.

## Deployment Helper Script

Create a `deploy.sh` script to automate deployment:

```bash
#!/bin/bash
set -e

PROJECT_ID="YOUR-PROJECT-ID"
REGION="us-central1"
PRODUCT="${1:-weaviate}"

if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh <product>"
    echo "Available products: weaviate, togetherai"
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
```

Make it executable:
```bash
chmod +x deploy.sh
```

Usage:
```bash
./deploy.sh weaviate
./deploy.sh togetherai
```

## Monitoring and Debugging

### View Logs

```bash
# Tail logs for a service
gcloud run services logs tail weaviate-docs-mcp --region us-central1

# View recent logs
gcloud run services logs read weaviate-docs-mcp --region us-central1 --limit 100
```

### Test the Server

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe weaviate-docs-mcp --region us-central1 --format 'value(status.url)')

# Test the MCP endpoint (should return MCP protocol messages)
curl -N -H "Accept: text/event-stream" "${SERVICE_URL}/mcp"
```

### Check Service Status

```bash
# List all deployed services
gcloud run services list --region us-central1

# Describe a specific service
gcloud run services describe weaviate-docs-mcp --region us-central1
```

## Updating Environment Variables

To update environment variables without redeploying:

```bash
gcloud run services update weaviate-docs-mcp \
    --region us-central1 \
    --set-env-vars WCD_KEY="new-api-key-here"
```

## Cost Optimization

Cloud Run charges based on:
- **Request time**: Pay only when handling requests
- **Memory and CPU**: Billed per 100ms of request handling
- **Requests**: First 2 million requests/month are free

Cost-saving tips:
1. Set `--min-instances 0` to scale to zero when idle
2. Use `--memory 512Mi` for basic workloads (adjust as needed)
3. Set `--timeout 300` to prevent runaway requests
4. Set `--max-instances` to cap costs during high traffic

## Security Considerations

### Secret Management

For production, use Google Secret Manager instead of environment variables:

```bash
# Create secrets
echo -n "your-weaviate-key" | gcloud secrets create wcd-key --data-file=-
echo -n "your-cohere-key" | gcloud secrets create cohere-api-key --data-file=-

# Deploy with secrets
gcloud run deploy weaviate-docs-mcp \
    --image ${IMAGE} \
    --set-secrets WCD_KEY=wcd-key:latest \
    --set-secrets COHERE_API_KEY=cohere-api-key:latest \
    # ... other flags
```

## Cleanup

To delete services and save costs:

```bash
# Delete a specific service
gcloud run services delete weaviate-docs-mcp --region us-central1

# Delete all MCP services
gcloud run services list --region us-central1 --format='value(metadata.name)' | \
    grep 'docs-mcp' | \
    xargs -I {} gcloud run services delete {} --region us-central1 --quiet
```

## Additional Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [MCP Remote Server Tutorial](https://cloud.google.com/run/docs/tutorials/deploy-remote-mcp-server)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
