# AWS Deployment Guide for PolicyEdgeAI

This document provides detailed instructions for deploying the PolicyEdgeAI platform to AWS using both manual deployment and GitHub Actions for CI/CD.

## Prerequisites

Before deployment, ensure you have:

1. An AWS account with administrative access
2. The AWS CLI installed and configured with your credentials
3. Docker installed (for local building and testing)
4. Your OpenAI and/or Anthropic API keys
5. A GitHub repository with the PolicyEdgeAI codebase

## Manual Deployment

### Step 1: Deploy Using CloudFormation

1. Navigate to the aws directory:
   ```bash
   cd aws
   ```

2. Run the deployment script:
   ```bash
   ./deploy.sh  # For standard deployment
   # OR
   ./deploy-https.sh  # For HTTPS deployment with SSL
   # OR
   ./deploy-production.sh  # For production deployment
   ```

3. The script will:
   - Create ECR repositories if they don't exist
   - Build and push Docker images
   - Deploy the CloudFormation stack
   - Output the endpoints for your application

### Step 2: Configure Secrets

1. Store your API keys in AWS Secrets Manager:
   ```bash
   aws secretsmanager create-secret \
     --name policyedgeai-secrets \
     --secret-string '{"OPENAI_API_KEY":"your_key_here","ANTHROPIC_API_KEY":"your_key_here","JWT_SECRET_KEY":"your_secure_key_here"}'
   ```

### Step 3: Verify Deployment

1. Check the status of your ECS services:
   ```bash
   aws ecs list-services --cluster PolicyEdgeAI-Cluster-prod
   aws ecs describe-services --cluster PolicyEdgeAI-Cluster-prod --services policyedgeai-api-service-prod
   ```

2. Access your endpoints (these will be in the CloudFormation outputs):
   - API: http://your-load-balancer-url.region.elb.amazonaws.com
   - Dashboard: http://your-load-balancer-url.region.elb.amazonaws.com:8501

## CI/CD Deployment Using GitHub Actions

### Step 1: Configure GitHub Repository Secrets

1. Add the following secrets to your GitHub repository:
   - `AWS_ROLE_ARN`: The ARN of an IAM role with deployment permissions
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ANTHROPIC_API_KEY`: Your Anthropic API key (optional)
   - `JWT_SECRET_KEY`: A secure key for JWT token signing
   - (Optional) `SLACK_WEBHOOK_URL`: For deployment notifications

### Step 2: Create AWS IAM Role for GitHub Actions

1. Create an IAM role with the following permissions:
   - AmazonECR-FullAccess
   - AmazonECS-FullAccess
   - CloudFormationFullAccess
   - AmazonDynamoDBFullAccess
   - AmazonS3FullAccess
   - IAMFullAccess (for service role creation)
   - SecretsManagerReadWrite
   - CloudWatchLogsFullAccess

2. Configure the role with a trust relationship for GitHub Actions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Federated": "arn:aws:iam::account-id:oidc-provider/token.actions.githubusercontent.com"
         },
         "Action": "sts:AssumeRoleWithWebIdentity",
         "Condition": {
           "StringEquals": {
             "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
           },
           "StringLike": {
             "token.actions.githubusercontent.com:sub": "repo:your-org/policyedgeai:*"
           }
         }
       }
     ]
   }
   ```

### Step 3: Set Up GitHub OIDC Provider

1. Create an OIDC provider in IAM:
   - Provider URL: `https://token.actions.githubusercontent.com`
   - Audience: `sts.amazonaws.com`

### Step 4: Push Code to Trigger Deployment

1. Push your code to the main branch:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. The GitHub Actions workflow will:
   - Run tests for pull requests
   - Build Docker images for the API and Dashboard
   - Push images to ECR
   - Deploy to ECS Fargate
   - Verify the deployment
   - Create deployment tags and send notifications

### Step 5: Monitor the Deployment

1. Check the Actions tab in your GitHub repository to monitor the deployment
2. Access the CloudWatch logs for your ECS tasks to troubleshoot any issues
3. Verify the application is running by accessing the API and Dashboard endpoints

## Infrastructure Overview

The deployment creates the following AWS resources:

- **Networking**: VPC, subnets, internet gateway, route tables
- **Compute**: ECS Fargate cluster, tasks, and services
- **Load Balancing**: Application Load Balancer and target groups
- **Storage**: S3 bucket for files, DynamoDB tables for data
- **Security**: IAM roles, security groups, Secrets Manager secret
- **Monitoring**: CloudWatch logs and dashboard

## Updating the Deployment

1. For manual updates:
   ```bash
   # Update ECR images
   cd aws
   ./deploy.sh  # Or appropriate script
   ```

2. For automatic updates via GitHub Actions:
   - Push changes to the main branch
   - The workflow will handle the update process

## Rollback Procedure

1. For GitHub Actions deployments:
   - Find the previous deployment tag in your repository
   - Check out that tag and push it to main, or
   - Manually update the ECS task definition to use the previous container image

2. For manual deployments:
   - Use the AWS Management Console to roll back the CloudFormation stack
   - Update the ECS service to use a previous task definition

## Cleanup

To remove all resources:

```bash
aws cloudformation delete-stack --stack-name policyedgeai-prod
```

Note: This will delete all resources including S3 buckets and DynamoDB tables, which will result in data loss. Make sure to back up any important data before cleanup.