# PolicyEdgeAI Deployment Steps

This guide provides step-by-step instructions to deploy PolicyEdgeAI to AWS ECS Fargate with HTTPS and a custom domain.

## Prerequisites

Before proceeding, ensure you have:

1. AWS account with administrator access
2. AWS CLI installed and configured (`aws configure`)
3. Docker installed locally
4. Domain registered in Amazon Route 53 (policyedgeai.com)
5. API keys for OpenAI and optionally Anthropic

## Step 1: Clone and Prepare Repository

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/your-org/policyedgeai.git
cd policyedgeai

# Copy environment variables example file
cp .env.example .env

# Edit .env with your actual API keys
nano .env  # or use your preferred editor
```

## Step 2: Create AWS Resources for Deployment

```bash
# Install AWS CLI if not already installed
# Mac: brew install awscli
# Windows: Download installer from AWS website
# Linux: sudo apt-get install awscli

# Configure AWS CLI
aws configure
# Enter your AWS Access Key, Secret Key, default region (us-east-1), and preferred output format (json)

# Create S3 bucket for deployment artifacts
aws s3 mb s3://policyedgeai-deployment-artifacts --region us-east-1

# Upload CloudFormation template
aws s3 cp aws/cloudformation-production.yaml s3://policyedgeai-deployment-artifacts/
```

## Step 3: Create ECR Repositories

```bash
# Create ECR repositories for API and Dashboard
aws ecr create-repository --repository-name policyedgeai-api
aws ecr create-repository --repository-name policyedgeai-dashboard

# Log in to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com
```

## Step 4: Build and Push Docker Images

```bash
# Get AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Build API image
docker build -t policyedgeai-api:latest -f api.Dockerfile .

# Tag API image
docker tag policyedgeai-api:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/policyedgeai-api:latest

# Push API image to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/policyedgeai-api:latest

# Build Dashboard image
docker build -t policyedgeai-dashboard:latest -f dashboard.Dockerfile .

# Tag Dashboard image
docker tag policyedgeai-dashboard:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/policyedgeai-dashboard:latest

# Push Dashboard image to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/policyedgeai-dashboard:latest
```

## Step 5: Deploy Using CloudFormation

```bash
# Request a certificate for your domain
aws acm request-certificate \
  --domain-name policyedgeai.com \
  --validation-method DNS \
  --subject-alternative-names "*.policyedgeai.com" \
  --region us-east-1

# Note the Certificate ARN and add DNS validation records to Route 53

# Create CloudFormation stack
aws cloudformation create-stack \
  --stack-name policyedgeai-prod \
  --template-url https://policyedgeai-deployment-artifacts.s3.amazonaws.com/cloudformation-production.yaml \
  --parameters \
    ParameterKey=Environment,ParameterValue=prod \
    ParameterKey=DomainName,ParameterValue=policyedgeai.com \
    ParameterKey=APISubdomain,ParameterValue=api \
    ParameterKey=DashboardSubdomain,ParameterValue=dashboard \
    ParameterKey=ECRRepositoryBase,ParameterValue=policyedgeai \
    ParameterKey=APIImageTag,ParameterValue=latest \
    ParameterKey=DashboardImageTag,ParameterValue=latest \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# Wait for stack creation to complete (may take 20-30 minutes)
aws cloudformation wait stack-create-complete --stack-name policyedgeai-prod
```

## Step 6: Store Secrets in Parameter Store

```bash
# Create a secure JWT secret key
export JWT_SECRET=$(openssl rand -hex 32)

# Store OpenAI API key
aws ssm put-parameter \
  --name "/policyedgeai/prod/openai-api-key" \
  --type SecureString \
  --value "YOUR_OPENAI_API_KEY" \
  --overwrite

# Store Anthropic API key (if you have one)
aws ssm put-parameter \
  --name "/policyedgeai/prod/anthropic-api-key" \
  --type SecureString \
  --value "YOUR_ANTHROPIC_API_KEY" \
  --overwrite

# Store JWT secret key
aws ssm put-parameter \
  --name "/policyedgeai/prod/jwt-secret-key" \
  --type SecureString \
  --value "$JWT_SECRET" \
  --overwrite
```

## Step 7: Verify Deployment

```bash
# Get the deployment outputs
aws cloudformation describe-stacks \
  --stack-name policyedgeai-prod \
  --query "Stacks[0].Outputs" \
  --output table

# Check if API service is running
aws ecs describe-services \
  --cluster PolicyEdgeAI-Cluster-prod \
  --services policyedgeai-api-service-prod \
  --query "services[0].status"

# Check if Dashboard service is running
aws ecs describe-services \
  --cluster PolicyEdgeAI-Cluster-prod \
  --services policyedgeai-dashboard-service-prod \
  --query "services[0].status"
```

## Step 8: Access Your Deployed Application

After successful deployment, access your application at:

- API: https://api.policyedgeai.com
- Dashboard: https://dashboard.policyedgeai.com
- Main Website: https://policyedgeai.com

## Troubleshooting

### Certificate Validation Issues

If the certificate fails to validate:

1. Go to AWS Certificate Manager in the us-east-1 region
2. Find your certificate and click on it
3. Look for the validation CNAME records you need to add
4. Add these records to Route 53:
   ```bash
   aws route53 change-resource-record-sets \
     --hosted-zone-id YOUR_HOSTED_ZONE_ID \
     --change-batch file://dns-validation.json
   ```

### Container Startup Issues

If containers fail to start, check the logs:

```bash
# Get the task IDs
aws ecs list-tasks \
  --cluster PolicyEdgeAI-Cluster-prod \
  --service-name policyedgeai-api-service-prod \
  --query "taskArns[0]" --output text

# View logs
aws logs get-log-events \
  --log-group-name /ecs/policyedgeai-api-prod \
  --log-stream-name ecs/api-container/TASK_ID_SUFFIX
```

### Parameter Store Issues

If the application can't access secrets, verify parameter permissions:

```bash
# Check that the task execution role has permission to read the parameters
aws iam get-policy-document --policy-id ECSTaskExecutionRole-PolicyEdgeAI
```

## Updating the Application

To update the application after code changes:

1. Rebuild and push the Docker images with the same process as Step 4
2. Force a new deployment:

```bash
# Redeploy API service
aws ecs update-service \
  --cluster PolicyEdgeAI-Cluster-prod \
  --service policyedgeai-api-service-prod \
  --force-new-deployment

# Redeploy Dashboard service
aws ecs update-service \
  --cluster PolicyEdgeAI-Cluster-prod \
  --service policyedgeai-dashboard-service-prod \
  --force-new-deployment
```

## Security Best Practices

1. **Enable MFA** for your AWS account
2. **Regularly rotate** your API keys
3. **Review CloudTrail** for suspicious activity
4. **Monitor application logs** in CloudWatch
5. **Use temporary credentials** when possible

## Cleanup

To remove all resources when no longer needed:

```bash
# Delete the CloudFormation stack
aws cloudformation delete-stack --stack-name policyedgeai-prod

# Delete ECR repositories and images
aws ecr delete-repository --repository-name policyedgeai-api --force
aws ecr delete-repository --repository-name policyedgeai-dashboard --force

# Delete Parameter Store parameters
aws ssm delete-parameter --name "/policyedgeai/prod/openai-api-key"
aws ssm delete-parameter --name "/policyedgeai/prod/anthropic-api-key"
aws ssm delete-parameter --name "/policyedgeai/prod/jwt-secret-key"

# Delete S3 bucket
aws s3 rb s3://policyedgeai-deployment-artifacts --force
```

## Next Steps

Consider setting up:

1. **CI/CD Pipeline**: Using GitHub Actions or AWS CodePipeline
2. **Monitoring**: Set up CloudWatch alarms for key metrics
3. **Backup Strategy**: For your DynamoDB tables and S3 data
4. **Cost Optimization**: Review and optimize resources