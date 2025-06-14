@echo off
setlocal enabledelayedexpansion

:: Crypto Trading Strategy Generator Deployment Script
echo =================================
echo Crypto Trading Strategy Generator
echo Deployment Script
echo =================================

:: Check if Docker is installed
where docker >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Docker is not installed.
    exit /b 1
)

:: Load environment variables from .env if it exists
if exist .env (
    echo Loading environment variables from .env file...
    for /f "tokens=*" %%a in (.env) do (
        set %%a
    )
) else (
    echo Warning: .env file not found. You'll need to provide environment variables manually.
)

:: Function to prompt for environment variables if not set
call :check_env_var "AZURE_API_KEY" "Azure OpenAI API Key"
call :check_env_var "AZURE_OPENAI_ENDPOINT" "Azure OpenAI Endpoint"
call :check_env_var "AZURE_DEPLOYMENT_NAME" "Azure Deployment Name"
call :check_env_var "BINANCE_TESTNET_API_KEY" "Binance API Key"
call :check_env_var "BINANCE_TESTNET_API_SECRET" "Binance API Secret"

:: Ask for deployment mode
echo Select deployment mode:
echo 1) Local Docker
echo 2) Docker Hub
echo 3) AWS ECR
set /p deployment_mode=Enter your choice (1-3): 

set IMAGE_NAME=crypto-strategy-generator
set TAG=latest

:: Build the Docker image
echo Building Docker image...
docker build -t %IMAGE_NAME%:%TAG% .

if "%deployment_mode%"=="1" (
    :: Local Docker deployment
    echo Starting local Docker container...
    docker run -d -p 8501:8501 ^
        -e AZURE_API_KEY="%AZURE_API_KEY%" ^
        -e AZURE_OPENAI_ENDPOINT="%AZURE_OPENAI_ENDPOINT%" ^
        -e AZURE_DEPLOYMENT_NAME="%AZURE_DEPLOYMENT_NAME%" ^
        -e BINANCE_TESTNET_API_KEY="%BINANCE_TESTNET_API_KEY%" ^
        -e BINANCE_TESTNET_API_SECRET="%BINANCE_TESTNET_API_SECRET%" ^
        --name crypto-strategy-app ^
        %IMAGE_NAME%:%TAG%
    
    echo Container started! Access the application at: http://localhost:8501
) else if "%deployment_mode%"=="2" (
    :: Docker Hub deployment
    set /p dockerhub_username=Enter your Docker Hub username: 
    
    :: Tag the image for Docker Hub
    set REMOTE_IMAGE=%dockerhub_username%/%IMAGE_NAME%:%TAG%
    docker tag %IMAGE_NAME%:%TAG% !REMOTE_IMAGE!
    
    :: Push to Docker Hub
    echo Pushing to Docker Hub as !REMOTE_IMAGE!...
    docker login
    docker push !REMOTE_IMAGE!
    
    echo Image pushed to Docker Hub successfully!
    echo To run the container:
    echo docker run -d -p 8501:8501 ^
    echo   -e AZURE_API_KEY=your_key ^
    echo   -e AZURE_OPENAI_ENDPOINT=your_endpoint ^
    echo   -e AZURE_DEPLOYMENT_NAME=your_deployment ^
    echo   -e BINANCE_TESTNET_API_KEY=your_binance_key ^
    echo   -e BINANCE_TESTNET_API_SECRET=your_binance_secret ^
    echo   !REMOTE_IMAGE!
) else if "%deployment_mode%"=="3" (
    :: AWS ECR deployment
    set /p aws_account_id=Enter your AWS account ID: 
    set /p aws_region=Enter AWS region: 
    
    :: Check if AWS CLI is installed
    where aws >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Error: AWS CLI is not installed.
        exit /b 1
    )
    
    :: Authenticate with AWS ECR
    echo Authenticating with AWS ECR...
    aws ecr get-login-password --region %aws_region% | docker login --username AWS --password-stdin %aws_account_id%.dkr.ecr.%aws_region%.amazonaws.com
    
    :: Create repository if it doesn't exist
    echo Creating/checking ECR repository...
    aws ecr describe-repositories --repository-names %IMAGE_NAME% --region %aws_region% || aws ecr create-repository --repository-name %IMAGE_NAME% --region %aws_region%
    
    :: Tag the image for ECR
    set REMOTE_IMAGE=%aws_account_id%.dkr.ecr.%aws_region%.amazonaws.com/%IMAGE_NAME%:%TAG%
    docker tag %IMAGE_NAME%:%TAG% !REMOTE_IMAGE!
    
    :: Push to ECR
    echo Pushing to AWS ECR as !REMOTE_IMAGE!...
    docker push !REMOTE_IMAGE!
    
    echo Image pushed to AWS ECR successfully!
    echo To deploy to ECS/Fargate, use the AWS console or CLI with the image: !REMOTE_IMAGE!
) else (
    echo Invalid option selected!
    exit /b 1
)

echo Deployment completed successfully!
goto :eof

:check_env_var
setlocal enabledelayedexpansion
set var_name=%~1
set var_desc=%~2
call set current_value=%%%var_name%%%

if "!current_value!"=="" (
    set /p new_value=Enter %var_desc%: 
    endlocal & set %var_name%=%new_value%
) else (
    echo %var_desc% is set to: !current_value:~0,5!****
    endlocal
)
goto :eof 