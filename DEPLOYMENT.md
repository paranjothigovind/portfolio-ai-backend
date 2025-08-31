# Deployment Guide for RAG Backend

This guide explains how to deploy the RAG backend to Azure using Docker and Azure Container Instances.

## Prerequisites

1. Azure subscription
2. Azure CLI installed
3. Docker installed (for building the image)

## Deployment Options

### Option 1: Deploy with Docker Build (Recommended)

1. **Build and push the Docker image**:
   ```bash
   # Login to Azure
   az login
   
   # Set variables
   RESOURCE_GROUP="rag-backend-rg"
   LOCATION="eastus"
   ACR_NAME="ragbackendregistry"
   
   # Create resource group
   az group create --name paranjothi-dev --location $LOCATION
   
   # Create Azure Container Registry
   az acr create --resource-group paranjothi-dev --name paranjothidev --sku Basic --admin-enabled true
   
   # Login to ACR
   az acr login --name paranjothidev
   
   # Build and push image
   docker build -t rag-backend .
   docker tag rag-backend paranjothidev.azurecr.io/rag-backend:v1.0
   docker push paranjothidev.azurecr.io/rag-backend:v1.0
   ```

2. **Deploy to Azure Container Instances**:
   ```bash
   # Get ACR credentials
   ACR_USERNAME=$(az acr credential show --name paranjothidev --query username --output tsv) // paranjothidev
   ACR_PASSWORD=$(az acr credential show --name paranjothidev --query passwords[0].value --output tsv)
   
   # Create container instance
   
   ```

### Option 2: Deploy with Pre-built Image

If you have a pre-built image in a registry:

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="rag-backend-rg"
LOCATION="eastus"

# Create resource group
az group create --name paranjothi-dev --location $LOCATION

# Create container instance
az container create \
    --resource-group paranjothi-dev \
    --name rag-backend-container \
    --image your-registry.com/rag-backend:v1.0 \
    --dns-name-label ragbackend \
    --ports 8000 \
    --environment-variables \
        AZURE_OPENAI_ENDPOINT="your-endpoint" \
        AZURE_OPENAI_API_KEY="your-api-key" \
        AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment-name"
```

## Environment Variables

Make sure to set these environment variables in your Azure Container Instance:

- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your Azure OpenAI deployment name

## Accessing the Application

After deployment, your application will be accessible at:
`http://ragbackend.<location>.azurecontainer.io:8000`

You can test it with:
```bash
curl http://ragbackend.<location>.azurecontainer.io:8000/health
```

## Monitoring and Logs

To check the status of your container:
```bash
az container show --resource-group rag-backend-rg --name rag-backend-container --query containers[0].instanceView.currentState.state
```

To view logs:
```bash
az container logs --resource-group rag-backend-rg --name rag-backend-container
```

## Updating the Application

To update your application:

1. Build and push a new version of your Docker image with a new tag
2. Update the container instance with the new image:
   ```bash
   az container create \
       --resource-group rag-backend-rg \
       --name rag-backend-container \
       --image paranjothidev.azurecr.io/rag-backend:v1.1 \
       --registry-login-server paranjothidev.azurecr.io \
       --registry-username $ACR_USERNAME \
       --registry-password $ACR_PASSWORD \
       --dns-name-label ragbackend \
       --ports 8000 \
       --environment-variables \
           AZURE_OPENAI_ENDPOINT="your-endpoint" \
           AZURE_OPENAI_API_KEY="your-api-key" \
           AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment-name"

