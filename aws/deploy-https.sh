#!/bin/bash
set -e

# Configuration (Edit these values)
AWS_REGION="us-east-1"  # Change to your preferred region
STACK_NAME="policyedgeai"
ECR_REPOSITORY_NAME="policyedgeai"
ENVIRONMENT="prod"  # dev, staging, or prod
IMAGE_TAG="latest"
DOMAIN_NAME="policyedgeai.com"  # Change to your domain
API_SUBDOMAIN="api"
DASHBOARD_SUBDOMAIN="dashboard"
GITHUB_OWNER="your-github-username"  # Change if using CI/CD
GITHUB_REPO="policyedgeai"  # Change if using CI/CD
GITHUB_BRANCH="main"  # Change if using CI/CD
ENABLE_CICD="false"  # Set to "true" to enable CI/CD pipeline

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}      PolicyEdgeAI - HTTPS Deployment Script          ${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo -e "${YELLOW}Region:${NC} ${AWS_REGION}"
echo -e "${YELLOW}Environment:${NC} ${ENVIRONMENT}"
echo -e "${YELLOW}Stack Name:${NC} ${STACK_NAME}-${ENVIRONMENT}"
echo -e "${YELLOW}Domain:${NC} ${DOMAIN_NAME}"
echo -e "${YELLOW}API Endpoint:${NC} ${API_SUBDOMAIN}.${DOMAIN_NAME}"
echo -e "${YELLOW}Dashboard Endpoint:${NC} ${DASHBOARD_SUBDOMAIN}.${DOMAIN_NAME}"
echo -e "${BLUE}=======================================================${NC}"
echo ""

# Check prerequisites
check_prerequisites() {
    echo -e "${GREEN}Checking prerequisites...${NC}"
    
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
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}Error: jq is not installed. Please install it first.${NC}"
        exit 1
    fi
    
    # Check AWS configuration
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}Error: AWS CLI is not configured properly. Please run 'aws configure'.${NC}"
        exit 1
    }
    
    echo -e "${GREEN}All prerequisites met.${NC}"
}

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
    docker build -t ${ECR_REPOSITORY_NAME}:${IMAGE_TAG} -f ../Dockerfile ..
    
    # Tag the image
    echo -e "${GREEN}Tagging Docker image...${NC}"
    docker tag ${ECR_REPOSITORY_NAME}:${IMAGE_TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}
    
    # Push the image to ECR
    echo -e "${GREEN}Pushing Docker image to ECR...${NC}"
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}
    
    echo -e "${GREEN}Docker image built and pushed successfully.${NC}"
    echo -e "${YELLOW}Image URI:${NC} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}"
}

# Check if domain exists in Route 53
check_domain() {
    echo -e "${GREEN}Checking if domain exists in Route 53...${NC}"
    
    if aws route53 list-hosted-zones-by-name --dns-name ${DOMAIN_NAME}. --max-items 1 | jq -r '.HostedZones[0].Name' | grep -q "^${DOMAIN_NAME}\.$"; then
        echo -e "${YELLOW}Domain ${DOMAIN_NAME} already exists in Route 53.${NC}"
        return 0
    else
        echo -e "${RED}Domain ${DOMAIN_NAME} does not exist in Route 53.${NC}"
        echo -e "${YELLOW}You need to register this domain in Route 53 or transfer it before deployment.${NC}"
        
        read -p "Do you want to continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}Deployment aborted.${NC}"
            exit 1
        fi
    fi
}

# Function to check if a certificate exists
check_certificate() {
    echo -e "${GREEN}Checking if certificate for ${DOMAIN_NAME} exists...${NC}"
    
    CERT_ARN=$(aws acm list-certificates --region ${AWS_REGION} | jq -r --arg domain "${DOMAIN_NAME}" '.CertificateSummaryList[] | select(.DomainName==$domain) | .CertificateArn')
    
    if [ -n "$CERT_ARN" ]; then
        echo -e "${YELLOW}Certificate for ${DOMAIN_NAME} already exists with ARN: ${CERT_ARN}${NC}"
        return 0
    else
        echo -e "${YELLOW}No certificate found for ${DOMAIN_NAME}.${NC}"
        echo -e "${YELLOW}A new certificate will be created as part of the CloudFormation stack.${NC}"
        echo -e "${YELLOW}Note: You will need to validate the certificate by adding DNS records to your domain.${NC}"
    fi
}

# Deploy CloudFormation stack
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
            --template-body file://cloudformation-https.yaml \
            --parameters \
                ParameterKey=Environment,ParameterValue=${ENVIRONMENT} \
                ParameterKey=DomainName,ParameterValue=${DOMAIN_NAME} \
                ParameterKey=APISubdomain,ParameterValue=${API_SUBDOMAIN} \
                ParameterKey=DashboardSubdomain,ParameterValue=${DASHBOARD_SUBDOMAIN} \
                ParameterKey=ECRRepositoryName,ParameterValue=${ECR_REPOSITORY_NAME} \
                ParameterKey=ECRImageTag,ParameterValue=${IMAGE_TAG} \
                ParameterKey=GitHubOwner,ParameterValue=${GITHUB_OWNER} \
                ParameterKey=GitHubRepo,ParameterValue=${GITHUB_REPO} \
                ParameterKey=GitHubBranch,ParameterValue=${GITHUB_BRANCH} \
                ParameterKey=EnableCICD,ParameterValue=${ENABLE_CICD} \
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
            --template-body file://cloudformation-https.yaml \
            --parameters \
                ParameterKey=Environment,ParameterValue=${ENVIRONMENT} \
                ParameterKey=DomainName,ParameterValue=${DOMAIN_NAME} \
                ParameterKey=APISubdomain,ParameterValue=${API_SUBDOMAIN} \
                ParameterKey=DashboardSubdomain,ParameterValue=${DASHBOARD_SUBDOMAIN} \
                ParameterKey=ECRRepositoryName,ParameterValue=${ECR_REPOSITORY_NAME} \
                ParameterKey=ECRImageTag,ParameterValue=${IMAGE_TAG} \
                ParameterKey=GitHubOwner,ParameterValue=${GITHUB_OWNER} \
                ParameterKey=GitHubRepo,ParameterValue=${GITHUB_REPO} \
                ParameterKey=GitHubBranch,ParameterValue=${GITHUB_BRANCH} \
                ParameterKey=EnableCICD,ParameterValue=${ENABLE_CICD} \
            --capabilities CAPABILITY_IAM \
            --region ${AWS_REGION}
        
        # Wait for stack creation to complete
        echo -e "${GREEN}Waiting for stack creation to complete...${NC}"
        aws cloudformation wait stack-create-complete --stack-name ${STACK_NAME}-${ENVIRONMENT} --region ${AWS_REGION}
    fi
    
    echo -e "${GREEN}CloudFormation stack deployed successfully.${NC}"
}

# Update Parameters in Parameter Store with actual values
update_parameters() {
    echo -e "${GREEN}Updating Parameters in Parameter Store...${NC}"
    
    echo -e "${YELLOW}You need to update the following parameters in Parameter Store:${NC}"
    echo -e "  - /policyedgeai/${ENVIRONMENT}/openai-api-key"
    echo -e "  - /policyedgeai/${ENVIRONMENT}/anthropic-api-key"
    echo -e "  - /policyedgeai/${ENVIRONMENT}/jwt-secret-key"
    
    # Generate a secure JWT secret key
    JWT_SECRET=$(openssl rand -hex 32)
    
    # Prompt for API keys
    read -p "Enter your OpenAI API key: " OPENAI_API_KEY
    read -p "Enter your Anthropic API key (or leave empty): " ANTHROPIC_API_KEY
    
    # Update parameters if provided
    if [ -n "$OPENAI_API_KEY" ]; then
        echo -e "${GREEN}Updating OpenAI API key...${NC}"
        aws ssm put-parameter \
            --name "/policyedgeai/${ENVIRONMENT}/openai-api-key" \
            --type SecureString \
            --value "${OPENAI_API_KEY}" \
            --overwrite \
            --region ${AWS_REGION}
    else
        echo -e "${YELLOW}OpenAI API key not provided. You'll need to set it manually later.${NC}"
    fi
    
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        echo -e "${GREEN}Updating Anthropic API key...${NC}"
        aws ssm put-parameter \
            --name "/policyedgeai/${ENVIRONMENT}/anthropic-api-key" \
            --type SecureString \
            --value "${ANTHROPIC_API_KEY}" \
            --overwrite \
            --region ${AWS_REGION}
    else
        echo -e "${YELLOW}Anthropic API key not provided. You'll need to set it manually later if needed.${NC}"
    fi
    
    # Always update JWT secret key with a secure value
    echo -e "${GREEN}Updating JWT secret key...${NC}"
    aws ssm put-parameter \
        --name "/policyedgeai/${ENVIRONMENT}/jwt-secret-key" \
        --type SecureString \
        --value "${JWT_SECRET}" \
        --overwrite \
        --region ${AWS_REGION}
    
    echo -e "${GREEN}Parameters updated successfully.${NC}"
}

# Get stack outputs
get_stack_outputs() {
    echo -e "${GREEN}Getting stack outputs...${NC}"
    
    aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME}-${ENVIRONMENT} \
        --query "Stacks[0].Outputs" \
        --region ${AWS_REGION} \
        --output table
}

# Main execution
echo -e "${GREEN}Starting deployment process...${NC}"

# Check prerequisites
check_prerequisites

# Check domain status
check_domain

# Check certificate status
check_certificate

# Create ECR repository
create_ecr_repository

# Build and push Docker image
build_and_push_image

# Deploy CloudFormation stack
deploy_cloudformation_stack

# Update parameters
update_parameters

# Get stack outputs
get_stack_outputs

echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Add DNS validation records if prompted for the ACM certificate"
echo -e "2. Verify that the endpoints are working:"
echo -e "   - API: https://${API_SUBDOMAIN}.${DOMAIN_NAME}"
echo -e "   - Dashboard: https://${DASHBOARD_SUBDOMAIN}.${DOMAIN_NAME}"
echo -e "   - Main site: https://${DOMAIN_NAME}"
echo -e "3. Check CloudWatch logs if you encounter any issues"
echo -e "${BLUE}=======================================================${NC}"