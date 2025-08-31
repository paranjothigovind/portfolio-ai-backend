#!/bin/bash

# Simple deployment script for RAG backend to Azure Container Instances
# This script assumes you have already built and pushed your Docker image to a registry

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
IMAGE_NAME="ragbackendregistry.azurecr.io/rag-backend:v1.0"

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create container instance with public image (you can change this to your private registry)
echo "Creating container instance..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image $IMAGE_NAME \
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