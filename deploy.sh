#!/bin/bash
set -e

# Crypto Trading Strategy Generator Deployment Script
# This script helps with building and deploying the application

# Display banner
echo "================================="
echo "Crypto Trading Strategy Generator"
echo "Deployment Script"
echo "================================="

# Check if Docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo "Error: Docker is not installed." >&2
  exit 1
fi

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo "Warning: .env file not found. You'll need to provide environment variables manually."
fi

# Function to prompt for environment variables if not set
check_env_var() {
    local var_name="$1"
    local var_desc="$2"
    local current_value="${!var_name}"
    
    if [ -z "$current_value" ]; then
        read -p "Enter $var_desc: " new_value
        eval "$var_name=\"$new_value\""
    else
        echo "$var_desc is set to: ${current_value:0:5}****" 
    fi
}

# Prompt for environment variables if not already set
check_env_var "AZURE_API_KEY" "Azure OpenAI API Key"
check_env_var "AZURE_OPENAI_ENDPOINT" "Azure OpenAI Endpoint"
check_env_var "AZURE_DEPLOYMENT_NAME" "Azure Deployment Name"
check_env_var "BINANCE_TESTNET_API_KEY" "Binance API Key"
check_env_var "BINANCE_TESTNET_API_SECRET" "Binance API Secret"

# Ask for deployment mode
echo "Select deployment mode:"
echo "1) Local Docker"
echo "2) Docker Hub"
echo "3) AWS ECR"
read -p "Enter your choice (1-3): " deployment_mode

IMAGE_NAME="crypto-strategy-generator"
TAG="latest"

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME:$TAG .

case $deployment_mode in
    1)
        # Local Docker deployment
        echo "Starting local Docker container..."
        docker run -d -p 8501:8501 \
            -e AZURE_API_KEY="$AZURE_API_KEY" \
            -e AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
            -e AZURE_DEPLOYMENT_NAME="$AZURE_DEPLOYMENT_NAME" \
            -e BINANCE_TESTNET_API_KEY="$BINANCE_TESTNET_API_KEY" \
            -e BINANCE_TESTNET_API_SECRET="$BINANCE_TESTNET_API_SECRET" \
            --name crypto-strategy-app \
            $IMAGE_NAME:$TAG
        
        echo "Container started! Access the application at: http://localhost:8501"
        ;;
        
    2)
        # Docker Hub deployment
        read -p "Enter your Docker Hub username: " dockerhub_username
        
        # Tag the image for Docker Hub
        REMOTE_IMAGE="$dockerhub_username/$IMAGE_NAME:$TAG"
        docker tag $IMAGE_NAME:$TAG $REMOTE_IMAGE
        
        # Push to Docker Hub
        echo "Pushing to Docker Hub as $REMOTE_IMAGE..."
        docker login
        docker push $REMOTE_IMAGE
        
        echo "Image pushed to Docker Hub successfully!"
        echo "To run the container:"
        echo "docker run -d -p 8501:8501 \\"
        echo "  -e AZURE_API_KEY=your_key \\"
        echo "  -e AZURE_OPENAI_ENDPOINT=your_endpoint \\"
        echo "  -e AZURE_DEPLOYMENT_NAME=your_deployment \\"
        echo "  -e BINANCE_TESTNET_API_KEY=your_binance_key \\"
        echo "  -e BINANCE_TESTNET_API_SECRET=your_binance_secret \\"
        echo "  $REMOTE_IMAGE"
        ;;
        
    3)
        # AWS ECR deployment
        read -p "Enter your AWS account ID: " aws_account_id
        read -p "Enter AWS region: " aws_region
        
        # Check if AWS CLI is installed
        if ! [ -x "$(command -v aws)" ]; then
            echo "Error: AWS CLI is not installed." >&2
            exit 1
        fi
        
        # Authenticate with AWS ECR
        echo "Authenticating with AWS ECR..."
        aws ecr get-login-password --region $aws_region | docker login --username AWS --password-stdin $aws_account_id.dkr.ecr.$aws_region.amazonaws.com
        
        # Create repository if it doesn't exist
        echo "Creating/checking ECR repository..."
        aws ecr describe-repositories --repository-names $IMAGE_NAME --region $aws_region || \
            aws ecr create-repository --repository-name $IMAGE_NAME --region $aws_region
        
        # Tag the image for ECR
        REMOTE_IMAGE="$aws_account_id.dkr.ecr.$aws_region.amazonaws.com/$IMAGE_NAME:$TAG"
        docker tag $IMAGE_NAME:$TAG $REMOTE_IMAGE
        
        # Push to ECR
        echo "Pushing to AWS ECR as $REMOTE_IMAGE..."
        docker push $REMOTE_IMAGE
        
        echo "Image pushed to AWS ECR successfully!"
        echo "To deploy to ECS/Fargate, use the AWS console or CLI with the image: $REMOTE_IMAGE"
        ;;
        
    *)
        echo "Invalid option selected!"
        exit 1
        ;;
esac

echo "Deployment completed successfully!" 