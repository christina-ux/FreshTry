# PolicyEdgeAI AWS Deployment Guide

This guide explains how to deploy the PolicyEdgeAI platform to AWS using Docker, ECS Fargate, and HTTPS with a custom domain.

## Architecture Overview

The deployment architecture includes:

- **Containerized Application**: FastAPI backend and Streamlit frontend in a single container
- **Secure Networking**: VPC with public and private subnets, NAT gateways
- **HTTPS Endpoints**: Custom domain with SSL certificates
- **High Availability**: Multiple availability zones, auto-scaling
- **Secret Management**: Parameters securely stored in AWS Parameter Store
- **Data Storage**: S3 for file storage, DynamoDB for database
- **Monitoring**: CloudWatch dashboard and logs

![Architecture Diagram](architecture-diagram.png)

## Prerequisites

Before you begin, ensure you have the following:

1. **AWS Account** with necessary permissions
2. **AWS CLI** installed and configured
3. **Docker** installed
4. **Domain Name** registered in Route 53 (or transferable)
5. **API Keys**:
   - OpenAI API key
   - (Optional) Anthropic API key

## Deployment Options

You have two deployment options:

1. **Basic Deployment**: Single-stack deployment with HTTP endpoints
2. **Production Deployment**: Full HTTPS deployment with custom domain

## Option 1: Basic Deployment

For a quick deployment with HTTP endpoints:

```bash
cd aws
./deploy.sh
```

This deploys:
- ECS Fargate with a single service
- Application Load Balancer with HTTP
- S3 and DynamoDB for storage
- CloudWatch for monitoring

## Option 2: Production Deployment with HTTPS

For a production deployment with HTTPS and custom domain:

### Step 1: Update Configuration

Edit the `deploy-https.sh` script to update your configuration:

```bash
# Configuration (Edit these values)
AWS_REGION="us-east-1"  # Change to your preferred region
DOMAIN_NAME="policyedgeai.com"  # Change to your domain
API_SUBDOMAIN="api"
DASHBOARD_SUBDOMAIN="dashboard"
```

### Step 2: Run Deployment Script

```bash
cd aws
./deploy-https.sh
```

This script will:
1. Check prerequisites
2. Verify domain registration in Route 53
3. Check for existing SSL certificates
4. Create ECR repository if needed
5. Build and push Docker image
6. Deploy CloudFormation stack
7. Set up secrets in Parameter Store
8. Display deployment outputs

### Step 3: DNS Validation for SSL Certificate

After running the script, you may need to add DNS validation records to verify your domain ownership for the SSL certificate:

1. In the AWS Console, go to AWS Certificate Manager
2. Find your certificate for your domain
3. Click "Create records in Route 53" to automatically add validation records

### Step 4: Verify Deployment

Once deployed, check that your endpoints are working:

- API: `https://api.yourdomain.com`
- Dashboard: `https://dashboard.yourdomain.com`
- Main site: `https://yourdomain.com`

## Continuous Deployment

### Option 1: AWS CodePipeline

If you enabled CI/CD in your deployment, AWS CodePipeline will automatically:
1. Pull code from your GitHub repository
2. Build a Docker image
3. Deploy to ECS

To enable this, set `ENABLE_CICD="true"` in your deployment script.

### Option 2: GitHub Actions

A GitHub Actions workflow file is provided at `.github/workflows/deploy.yml`.

To use it:

1. Create a GitHub repository for your code
2. Add the following secrets to your repository:
   - `AWS_ROLE_ARN`: ARN of an IAM role with permissions to deploy

3. Push your code to GitHub to trigger deployment

## Security Configuration

### Parameter Store Secrets

Your secrets are stored in AWS Parameter Store at:
- `/policyedgeai/{environment}/openai-api-key`
- `/policyedgeai/{environment}/anthropic-api-key`
- `/policyedgeai/{environment}/jwt-secret-key`

You can update them using:

```bash
aws ssm put-parameter \
  --name "/policyedgeai/prod/openai-api-key" \
  --type SecureString \
  --value "your-key-here" \
  --overwrite
```

### IAM Roles and Permissions

The deployment creates these roles:
- `ECSTaskExecutionRole`: For pulling images and accessing secrets
- `ECSTaskRole`: For accessing AWS services from containers

### MFA and Access Control

For additional security:
1. Enable MFA for all AWS users
2. Use AWS Organizations with SCP policies
3. Implement IP-based restrictions on the ALB if needed

## Monitoring and Logging

### CloudWatch Dashboard

A CloudWatch dashboard is created to monitor:
- CPU and memory utilization
- Request counts and response times
- Error rates

Access it at:
`https://console.aws.amazon.com/cloudwatch/home?region={region}#dashboards:name=PolicyEdgeAI-Dashboard-{environment}`

### Logs

Container logs are available in CloudWatch Logs:
- `/ecs/policyedgeai-api-{environment}`
- `/ecs/policyedgeai-ui-{environment}`

## Updating the Deployment

### Manual Updates

1. Update your code
2. Rebuild and push the Docker image
3. Update the ECS service:

```bash
aws ecs update-service \
  --cluster PolicyEdgeAI-Cluster-prod \
  --service policyedgeai-service-prod \
  --force-new-deployment
```

### Automated Updates

If you've set up CI/CD, just push to your main branch.

## Scaling Configuration

The default deployment includes auto-scaling based on CPU utilization.

To adjust scaling settings:

```bash
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/PolicyEdgeAI-Cluster-prod/policyedgeai-service-prod \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-tracking-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{"TargetValue": 70.0, "PredefinedMetricSpecification": {"PredefinedMetricType": "ECSServiceAverageCPUUtilization"}}'
```

## Troubleshooting

### Common Issues

1. **Certificate Validation Failures**:
   - Check Route 53 for validation records
   - Ensure domain ownership

2. **Container Startup Failures**:
   - Check CloudWatch Logs for error messages
   - Verify API keys in Parameter Store

3. **Networking Issues**:
   - Confirm security group rules allow traffic
   - Check ALB health check configuration

### Getting Help

For additional assistance:
- Check CloudWatch Logs
- Review ECS Task status in the AWS Console
- Use AWS CloudTrail for API diagnostics

## Cleanup

To remove all resources:

```bash
aws cloudformation delete-stack \
  --stack-name policyedgeai-prod \
  --region us-east-1
```

Note: This will delete all application data. Back up any important data beforehand.

## Advanced Configuration

### Custom Container Configuration

To customize the container configuration, edit the CloudFormation template:
- `TaskDefinition`: Container settings and environment variables
- `ECSService`: Service configuration and load balancing

### Network Security Customization

To enhance network security:
- Adjust security group ingress rules
- Configure WAF for API protection
- Set up AWS Shield for DDoS protection

### Multiple Environments

To set up multiple environments (dev, staging, prod):
1. Create separate CloudFormation stacks with different environment parameters
2. Use different subdomains for each environment

## Estimated Costs

Approximate monthly costs for a standard deployment:
- ECS Fargate: $40-80/month (2 tasks, 1CPU, 2GB memory)
- ALB: $20-30/month
- NAT Gateway: $30-40/month
- S3 and DynamoDB: $5-20/month depending on usage
- CloudWatch: $10-20/month

Total: $105-190/month for a standard deployment

To reduce costs:
- Use Fargate Spot for non-production environments
- Consolidate to a single ALB
- Implement auto-scaling to reduce capacity during off-hours