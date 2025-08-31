#!/bin/bash

# Deployment script for RAG backend to Azure Container Instances

# Check if Azure CLI is installed
if ! command -v az &> /dev/null
then
    echo "Azure CLI is not installed. Please install it first: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure (if not already logged in)
echo "Logging in to Azure..."
az login

# Set variables
RESOURCE_GROUP="rag-backend-rg"
LOCATION="eastus"
CONTAINER_NAME="rag-backend-container"
ACR_NAME="ragbackendregistry"
IMAGE_NAME="rag-backend"
TAG="v1.0"

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
echo "ACR Login Server: $ACR_LOGIN_SERVER"

# Login to ACR
echo "Logging in to ACR..."
az acr login --name $ACR_NAME

# Build and push Docker image to ACR
echo "Building and pushing Docker image to ACR..."
# Note: This assumes Docker is installed and running
docker build -t $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG .
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Create container instance
echo "Creating container instance..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG \
    --registry-login-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --dns-name-label ragbackend \
    --ports 8000 \
    --environment-variables \
        AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
        AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
        AZURE_OPENAI_DEPLOYMENT_NAME=$AZURE_OPENAI_DEPLOYMENT_NAME

# Show container status
echo "Checking container status..."
az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query containers[0].instanceView.currentState.state

# Get container logs
echo "Getting container logs..."
az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME

echo "Deployment completed!"
echo "Access your application at: http://ragbackend.$LOCATION.azurecontainer.io:8000"