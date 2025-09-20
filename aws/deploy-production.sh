#!/bin/bash
set -e

# Configuration (Edit these values)
AWS_REGION="us-east-1"  # Change to your preferred region
STACK_NAME="policyedgeai"
ECR_REPOSITORY_BASE="policyedgeai"
ENVIRONMENT="prod"  # dev, staging, or prod
API_IMAGE_TAG="latest"
DASHBOARD_IMAGE_TAG="latest"
DOMAIN_NAME="policyedgeai.com"  # Change to your domain
API_SUBDOMAIN="api"
DASHBOARD_SUBDOMAIN="dashboard"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}   PolicyEdgeAI - Production Deployment Script        ${NC}"
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
    fi
    
    echo -e "${GREEN}All prerequisites met.${NC}"
}

# Function to get AWS account ID
get_aws_account_id() {
    aws sts get-caller-identity --query "Account" --output text
}

# Create ECR repositories if they don't exist
create_ecr_repositories() {
    echo -e "${GREEN}Checking if ECR repositories exist...${NC}"
    
    # API repository
    if aws ecr describe-repositories --repository-names ${ECR_REPOSITORY_BASE}-api --region ${AWS_REGION} &> /dev/null; then
        echo -e "${YELLOW}ECR repository ${ECR_REPOSITORY_BASE}-api already exists.${NC}"
    else
        echo -e "${GREEN}Creating ECR repository ${ECR_REPOSITORY_BASE}-api...${NC}"
        aws ecr create-repository --repository-name ${ECR_REPOSITORY_BASE}-api --region ${AWS_REGION}
        echo -e "${GREEN}ECR repository created successfully.${NC}"
    fi
    
    # Dashboard repository
    if aws ecr describe-repositories --repository-names ${ECR_REPOSITORY_BASE}-dashboard --region ${AWS_REGION} &> /dev/null; then
        echo -e "${YELLOW}ECR repository ${ECR_REPOSITORY_BASE}-dashboard already exists.${NC}"
    else
        echo -e "${GREEN}Creating ECR repository ${ECR_REPOSITORY_BASE}-dashboard...${NC}"
        aws ecr create-repository --repository-name ${ECR_REPOSITORY_BASE}-dashboard --region ${AWS_REGION}
        echo -e "${GREEN}ECR repository created successfully.${NC}"
    fi
}

# Build and push API Docker image
build_and_push_api_image() {
    echo -e "${GREEN}Building and pushing API Docker image...${NC}"
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(get_aws_account_id)
    
    # Authenticate Docker to ECR
    echo -e "${GREEN}Authenticating Docker to ECR...${NC}"
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
    
    # Build the API Docker image
    echo -e "${GREEN}Building API Docker image...${NC}"
    docker build -t ${ECR_REPOSITORY_BASE}-api:${API_IMAGE_TAG} \
        -f ../api.Dockerfile \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        ..
    
    # Tag the API image
    echo -e "${GREEN}Tagging API Docker image...${NC}"
    docker tag ${ECR_REPOSITORY_BASE}-api:${API_IMAGE_TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_BASE}-api:${API_IMAGE_TAG}
    
    # Push the API image to ECR
    echo -e "${GREEN}Pushing API Docker image to ECR...${NC}"
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_BASE}-api:${API_IMAGE_TAG}
    
    echo -e "${GREEN}API Docker image built and pushed successfully.${NC}"
    echo -e "${YELLOW}API Image URI:${NC} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_BASE}-api:${API_IMAGE_TAG}"
}

# Build and push Dashboard Docker image
build_and_push_dashboard_image() {
    echo -e "${GREEN}Building and pushing Dashboard Docker image...${NC}"
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(get_aws_account_id)
    
    # Authenticate Docker to ECR (if not already done)
    if ! docker info | grep -q "Username: AWS"; then
        echo -e "${GREEN}Authenticating Docker to ECR...${NC}"
        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
    fi
    
    # Build the Dashboard Docker image
    echo -e "${GREEN}Building Dashboard Docker image...${NC}"
    docker build -t ${ECR_REPOSITORY_BASE}-dashboard:${DASHBOARD_IMAGE_TAG} \
        -f ../dashboard.Dockerfile \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        ..
    
    # Tag the Dashboard image
    echo -e "${GREEN}Tagging Dashboard Docker image...${NC}"
    docker tag ${ECR_REPOSITORY_BASE}-dashboard:${DASHBOARD_IMAGE_TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_BASE}-dashboard:${DASHBOARD_IMAGE_TAG}
    
    # Push the Dashboard image to ECR
    echo -e "${GREEN}Pushing Dashboard Docker image to ECR...${NC}"
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_BASE}-dashboard:${DASHBOARD_IMAGE_TAG}
    
    echo -e "${GREEN}Dashboard Docker image built and pushed successfully.${NC}"
    echo -e "${YELLOW}Dashboard Image URI:${NC} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_BASE}-dashboard:${DASHBOARD_IMAGE_TAG}"
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
        
        # Check if certificate is validated
        CERT_STATUS=$(aws acm describe-certificate --certificate-arn ${CERT_ARN} --query 'Certificate.Status' --output text)
        if [ "$CERT_STATUS" != "ISSUED" ]; then
            echo -e "${RED}Certificate exists but is not validated (Status: ${CERT_STATUS}).${NC}"
            echo -e "${YELLOW}You need to validate the certificate before deployment.${NC}"
            echo -e "${YELLOW}Check the certificate in AWS Certificate Manager and follow the validation steps.${NC}"
            
            read -p "Do you want to continue anyway? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${RED}Deployment aborted.${NC}"
                exit 1
            fi
        fi
        
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
            --template-body file://cloudformation-production.yaml \
            --parameters \
                ParameterKey=Environment,ParameterValue=${ENVIRONMENT} \
                ParameterKey=DomainName,ParameterValue=${DOMAIN_NAME} \
                ParameterKey=APISubdomain,ParameterValue=${API_SUBDOMAIN} \
                ParameterKey=DashboardSubdomain,ParameterValue=${DASHBOARD_SUBDOMAIN} \
                ParameterKey=ECRRepositoryBase,ParameterValue=${ECR_REPOSITORY_BASE} \
                ParameterKey=APIImageTag,ParameterValue=${API_IMAGE_TAG} \
                ParameterKey=DashboardImageTag,ParameterValue=${DASHBOARD_IMAGE_TAG} \
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
            --template-body file://cloudformation-production.yaml \
            --parameters \
                ParameterKey=Environment,ParameterValue=${ENVIRONMENT} \
                ParameterKey=DomainName,ParameterValue=${DOMAIN_NAME} \
                ParameterKey=APISubdomain,ParameterValue=${API_SUBDOMAIN} \
                ParameterKey=DashboardSubdomain,ParameterValue=${DASHBOARD_SUBDOMAIN} \
                ParameterKey=ECRRepositoryBase,ParameterValue=${ECR_REPOSITORY_BASE} \
                ParameterKey=APIImageTag,ParameterValue=${API_IMAGE_TAG} \
                ParameterKey=DashboardImageTag,ParameterValue=${DASHBOARD_IMAGE_TAG} \
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

# Create Docker files for API and Dashboard
create_dockerfiles() {
    echo -e "${GREEN}Creating Dockerfiles for API and Dashboard...${NC}"
    
    # API Dockerfile
    cat > ../api.Dockerfile << 'EOF'
FROM python:3.9-slim

# Build arguments
ARG BUILD_DATE=unknown
ARG GITHUB_SHA=unknown
ARG GITHUB_REF=unknown

# Labels for container metadata
LABEL org.opencontainers.image.created=${BUILD_DATE} \
      org.opencontainers.image.revision=${GITHUB_SHA} \
      maintainer="DevOps <devops@example.com>" \
      app.kubernetes.io/name="policyedgeai-api" \
      app.kubernetes.io/version="1.0.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    curl \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p data/uploads data/reports data/dashboard data/scoring data/uploads/processed logs

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    AWS_REGION=us-east-1 \
    LOG_LEVEL=INFO \
    APP_ENV=production

# Save build info for diagnostics
RUN echo "Build Date: ${BUILD_DATE}" > /app/build_info.txt && \
    echo "Build: ${GITHUB_SHA}" >> /app/build_info.txt && \
    echo "Branch/Tag: ${GITHUB_REF}" >> /app/build_info.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set the default health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Start API server
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT --log-level ${LOG_LEVEL,,}"]
EOF

    # Dashboard Dockerfile
    cat > ../dashboard.Dockerfile << 'EOF'
FROM python:3.9-slim

# Build arguments
ARG BUILD_DATE=unknown
ARG GITHUB_SHA=unknown
ARG GITHUB_REF=unknown

# Labels for container metadata
LABEL org.opencontainers.image.created=${BUILD_DATE} \
      org.opencontainers.image.revision=${GITHUB_SHA} \
      maintainer="DevOps <devops@example.com>" \
      app.kubernetes.io/name="policyedgeai-dashboard" \
      app.kubernetes.io/version="1.0.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_PORT=8501 \
    API_URL=http://localhost:8000 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Save build info for diagnostics
RUN echo "Build Date: ${BUILD_DATE}" > /app/build_info.txt && \
    echo "Build: ${GITHUB_SHA}" >> /app/build_info.txt && \
    echo "Branch/Tag: ${GITHUB_REF}" >> /app/build_info.txt

# Copy Streamlit application
COPY streamlit_app.py .

# Expose port
EXPOSE 8501

# Set the default health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8501/ || exit 1

# Start Streamlit server
CMD ["sh", "-c", "streamlit run streamlit_app.py --server.port=$STREAMLIT_PORT --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false"]
EOF

    echo -e "${GREEN}Dockerfiles created successfully.${NC}"
}

# Main execution
echo -e "${GREEN}Starting deployment process...${NC}"

# Check prerequisites
check_prerequisites

# Create Dockerfiles
create_dockerfiles

# Check domain status
check_domain

# Check certificate status
check_certificate

# Create ECR repositories
create_ecr_repositories

# Build and push Docker images
build_and_push_api_image
build_and_push_dashboard_image

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