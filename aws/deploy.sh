#!/bin/bash
set -e

# Configuration
AWS_REGION="us-east-1"  # Change to your preferred region
STACK_NAME="policyedgeai"
ECR_REPOSITORY_NAME="policyedgeai"
ENVIRONMENT="dev"  # dev, staging, or prod
IMAGE_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install it first.${NC}"
    exit 1
fi

# Print header
echo -e "${GREEN}=== PolicyEdgeAI Deployment Script ===${NC}"
echo -e "${YELLOW}Region: ${AWS_REGION}${NC}"
echo -e "${YELLOW}Environment: ${ENVIRONMENT}${NC}"
echo -e "${YELLOW}Stack Name: ${STACK_NAME}-${ENVIRONMENT}${NC}"
echo ""

# Function to get AWS account ID
get_aws_account_id() {
    aws sts get-caller-identity --query "Account" --output text
}

# Create ECR repository if it doesn't exist
create_ecr_repository() {
    echo -e "${GREEN}Checking if ECR repository exists...${NC}"
    
    if aws ecr describe-repositories --repository-names ${ECR_REPOSITORY_NAME} --region ${AWS_REGION} &> /dev/null; then
        echo -e "${YELLOW}ECR repository ${ECR_REPOSITORY_NAME} already exists.${NC}"
    else
        echo -e "${GREEN}Creating ECR repository ${ECR_REPOSITORY_NAME}...${NC}"
        aws ecr create-repository --repository-name ${ECR_REPOSITORY_NAME} --region ${AWS_REGION}
        echo -e "${GREEN}ECR repository created successfully.${NC}"
    fi
}

# Build and push Docker image
build_and_push_image() {
    echo -e "${GREEN}Building and pushing Docker image...${NC}"
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(get_aws_account_id)
    
    # Authenticate Docker to ECR
    echo -e "${GREEN}Authenticating Docker to ECR...${NC}"
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
    
    # Build the Docker image
    echo -e "${GREEN}Building Docker image...${NC}"
    docker build -t ${ECR_REPOSITORY_NAME}:${IMAGE_TAG} -f Dockerfile ..
    
    # Tag the image
    echo -e "${GREEN}Tagging Docker image...${NC}"
    docker tag ${ECR_REPOSITORY_NAME}:${IMAGE_TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}
    
    # Push the image to ECR
    echo -e "${GREEN}Pushing Docker image to ECR...${NC}"
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}
    
    echo -e "${GREEN}Docker image built and pushed successfully.${NC}"
    
    echo "Image URI: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}"
}

# Create or update CloudFormation stack
deploy_cloudformation_stack() {
    echo -e "${GREEN}Deploying CloudFormation stack...${NC}"
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(get_aws_account_id)
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name ${STACK_NAME}-${ENVIRONMENT} --region ${AWS_REGION} &> /dev/null; then
        echo -e "${YELLOW}Updating existing CloudFormation stack...${NC}"
        
        # Update the stack
        aws cloudformation update-stack \
            --stack-name ${STACK_NAME}-${ENVIRONMENT} \
            --template-body file://cloudformation.yaml \
            --parameters \
                ParameterKey=Environment,ParameterValue=${ENVIRONMENT} \
                ParameterKey=ECRRepositoryName,ParameterValue=${ECR_REPOSITORY_NAME} \
                ParameterKey=ECRImageTag,ParameterValue=${IMAGE_TAG} \
            --capabilities CAPABILITY_IAM \
            --region ${AWS_REGION}
        
        # Wait for stack update to complete
        echo -e "${GREEN}Waiting for stack update to complete...${NC}"
        aws cloudformation wait stack-update-complete --stack-name ${STACK_NAME}-${ENVIRONMENT} --region ${AWS_REGION}
        
    else
        echo -e "${YELLOW}Creating new CloudFormation stack...${NC}"
        
        # Create the stack
        aws cloudformation create-stack \
            --stack-name ${STACK_NAME}-${ENVIRONMENT} \
            --template-body file://cloudformation.yaml \
            --parameters \
                ParameterKey=Environment,ParameterValue=${ENVIRONMENT} \
                ParameterKey=ECRRepositoryName,ParameterValue=${ECR_REPOSITORY_NAME} \
                ParameterKey=ECRImageTag,ParameterValue=${IMAGE_TAG} \
            --capabilities CAPABILITY_IAM \
            --region ${AWS_REGION}
        
        # Wait for stack creation to complete
        echo -e "${GREEN}Waiting for stack creation to complete...${NC}"
        aws cloudformation wait stack-create-complete --stack-name ${STACK_NAME}-${ENVIRONMENT} --region ${AWS_REGION}
    fi
    
    echo -e "${GREEN}CloudFormation stack deployed successfully.${NC}"
}

# Get stack outputs
get_stack_outputs() {
    echo -e "${GREEN}Getting stack outputs...${NC}"
    
    aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME}-${ENVIRONMENT} \
        --query "Stacks[0].Outputs" \
        --region ${AWS_REGION}
}

# Main execution
echo -e "${GREEN}Starting deployment process...${NC}"

# Create ECR repository
create_ecr_repository

# Build and push Docker image
build_and_push_image

# Deploy CloudFormation stack
deploy_cloudformation_stack

# Get stack outputs
get_stack_outputs

echo -e "${GREEN}Deployment completed successfully!${NC}"