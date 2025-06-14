<#
.SYNOPSIS
Deploy the Crypto Trading Strategy Generator Docker image to Azure Web App for Containers.

.DESCRIPTION
This script logs into Azure, creates a resource group, an Azure Container Registry (ACR), builds and pushes the Docker image,
creates an App Service plan and Web App for Containers, sets environment variables, and opens the site.

.PARAMETER ResourceGroupName
Name of the Azure Resource Group to create or use.

.PARAMETER AcrName
Name of the Azure Container Registry to create or use.

.PARAMETER PlanName
Name of the App Service plan to create or use.

.PARAMETER WebAppName
Globally unique name for the Web App to create.

.PARAMETER Location
Azure region for the resources (default: swedencentral).

.EXAMPLE
.\\deploy-azure.ps1 -ResourceGroupName CryptoRG -AcrName CryptoAcr -PlanName CryptoPlan -WebAppName MyCryptoApp
#>

param(
    [Parameter(Mandatory=$true)][string]$ResourceGroupName,
    [Parameter(Mandatory=$true)][string]$AcrName,
    [Parameter(Mandatory=$true)][string]$PlanName,
    [Parameter(Mandatory=$true)][string]$WebAppName,
    [string]$Location = "swedencentral"
)

Write-Host "Logging in to Azure..."
az login | Out-Null

Write-Host "Creating Resource Group: $ResourceGroupName in $Location..."
az group create --name $ResourceGroupName --location $Location | Out-Null

Write-Host "Creating or updating ACR: $AcrName..."
az acr create --resource-group $ResourceGroupName --name $AcrName --sku Basic --admin-enabled true | Out-Null

Write-Host "Logging in to ACR..."
az acr login --name $AcrName | Out-Null

$ImageName = "$AcrName.azurecr.io/crypto-strategy:latest"
Write-Host "Building Docker image: $ImageName..."
docker build -t $ImageName .

Write-Host "Pushing Docker image to ACR..."
docker push $ImageName

Write-Host "Creating App Service Plan: $PlanName..."
az appservice plan create --name $PlanName --resource-group $ResourceGroupName --is-linux --sku B1 | Out-Null

Write-Host "Creating Web App for Containers: $WebAppName..."
az webapp create --resource-group $ResourceGroupName --plan $PlanName --name $WebAppName --deployment-container-image-name $ImageName | Out-Null

Write-Host "Configuring application settings..."
# Reads Azure credentials from environment variables
az webapp config appsettings set \
  --resource-group $ResourceGroupName \
  --name $WebAppName \
  --settings \
    AZURE_API_KEY="$Env:AZURE_API_KEY" \
    AZURE_OPENAI_ENDPOINT="$Env:AZURE_OPENAI_ENDPOINT" \
    AZURE_DEPLOYMENT_NAME="$Env:AZURE_DEPLOYMENT_NAME" | Out-Null

Write-Host "Deployment complete. Opening Web App in browser..."
az webapp browse --resource-group $ResourceGroupName --name $WebAppName 