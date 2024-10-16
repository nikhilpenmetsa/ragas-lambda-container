#!/bin/bash

# Load the variables from the setenv.sh file
if [ ! -f setenv.sh ]; then
    echo "Error: setenv.sh file not found"
    exit 1
fi
source setenv.sh



# Build the Docker image
echo "Building Docker image..."
if ! docker build -t rag-eval-container-func ../lambda/; then
    echo "Error: Docker build failed"
    exit 1
fi

# Check if ECR repository exists
echo "Checking if ECR repository exists..."
ECR_REPO_URI=$(aws ecr describe-repositories --repository-names $ECR_REPO_NAME --profile "$PROFILE" --query 'repositories[0].repositoryUri' --output text 2>&1)

if [ $? -eq 0 ]; then
    echo "Repository $ECR_REPO_NAME already exists"
else
    if [[ $ECR_REPO_URI == *"RepositoryNotFoundException"* ]]; then
        echo "Repository does not exist. Creating ECR repository..."
        ECR_REPO_URI=$(aws ecr create-repository --repository-name $ECR_REPO_NAME --profile "$PROFILE" --query 'repository.repositoryUri' --output text)
        if [ $? -eq 0 ]; then
            echo "ECR repository created successfully"
        else
            echo "Error creating ECR repository: $ECR_REPO_URI"
            exit 1
        fi
    else
        echo "Error checking ECR repository: $ECR_REPO_URI"
        exit 1
    fi
fi

echo "ECR Repository URI: $ECR_REPO_URI"

# # Create ECR repository
# echo "Creating ECR repository..."
# ECR_REPO_URI=$(aws ecr create-repository --repository-name $ECR_REPO_NAME --profile "$PROFILE" --query 'repository.repositoryUri' --output text 2>&1)
# if [ $? -ne 0 ]; then
#     if [[ $ECR_REPO_URI == *"RepositoryAlreadyExistsException"* ]]; then
#         echo "Repository already exists"
#     else
#         echo "Error creating ECR repository: $ECR_REPO_URI"
#         exit 1
#     fi
# fi

# Extract account ID and region from ECR_REPO_URI
ACCOUNT_ID=$(echo "$ECR_REPO_URI" | awk -F/ '{print $1}' | awk -F. '{print $1}')
AWS_REGION=$(echo "$ECR_REPO_URI" | awk -F/ '{print $1}' | awk -F. '{print $4}')
url=https://${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Login to ECR
echo "Logging in to ECR..."
if ! aws ecr get-login-password --profile "$PROFILE" --region ${AWS_REGION} | docker login --username AWS --password-stdin ${url}; then
    echo "Error: Failed to login to ECR"
    exit 1
fi

# Tag and push the Docker image
echo "Tagging Docker image..."
if ! docker tag rag-eval-container-func:latest ${ECR_REPO_URI}:latest; then
    echo "Error: Failed to tag Docker image"
    exit 1
fi

echo "Pushing Docker image to ECR..."
if ! docker push ${ECR_REPO_URI}:latest; then
    echo "Error: Failed to push Docker image to ECR"
    exit 1
fi

echo "Docker image successfully pushed to ${ECR_REPO_URI}:latest"