# GitHub Actions CI/CD Setup for PolicyEdgeAI

This guide explains how to set up the GitHub Actions workflow for continuous integration and deployment to AWS ECS.

## Overview

The CI/CD pipeline will:

1. Run tests on pull requests
2. Build and push Docker images to ECR on merges to main
3. Deploy the new images to ECS
4. Verify the deployment
5. Send notifications (optional)

## Prerequisites

Before setting up GitHub Actions, you need:

1. A GitHub repository for your code
2. An AWS account with appropriate permissions
3. The PolicyEdgeAI application deployed using the AWS CloudFormation template

## Setting Up IAM for GitHub Actions

GitHub Actions needs permission to access your AWS resources. The recommended approach is to use OpenID Connect (OIDC) for secure authentication without long-lived credentials.

### Step 1: Create an IAM OIDC Provider

1. In the AWS Console, go to IAM > Identity providers
2. Click "Add provider"
3. Select "OpenID Connect"
4. Enter Provider URL: `https://token.actions.githubusercontent.com`
5. Enter Audience: `sts.amazonaws.com`
6. Click "Get thumbprint" and then "Add provider"

### Step 2: Create an IAM Role for GitHub Actions

1. Go to IAM > Roles
2. Click "Create role"
3. Select "Web identity"
4. Choose the OIDC provider you created
5. For "Audience", select `sts.amazonaws.com`
6. Add the following condition to restrict access to your repository:
   ```
   {
     "StringLike": {
       "token.actions.githubusercontent.com:sub": "repo:your-github-username/policyedgeai:*"
     }
   }
   ```
7. Click "Next"
8. Attach the following policies:
   - `AmazonECR-FullAccess`
   - `AmazonECS-FullAccess`
   - `AmazonSSMReadOnlyAccess`
   - Create a custom policy with permissions to list and describe ECS tasks, services, and CloudWatch logs
9. Name the role `GitHub-Actions-PolicyEdgeAI` and create it
10. Note the ARN of the role for later use

## Setting Up GitHub Secrets

You need to add the AWS role ARN as a secret in your GitHub repository:

1. Go to your GitHub repository
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add the following secrets:
   - Name: `AWS_ROLE_ARN`
   - Value: The ARN of the IAM role you created (e.g., `arn:aws:iam::123456789012:role/GitHub-Actions-PolicyEdgeAI`)
5. (Optional) If you want Slack notifications, add:
   - Name: `SLACK_WEBHOOK_URL`
   - Value: Your Slack webhook URL

## GitHub Actions Workflow

The workflow file `.github/workflows/deploy.yml` includes:

### Test Job

Runs on pull requests to validate code quality:
- Checks out code
- Sets up Python
- Installs dependencies
- Runs tests
- Uploads code coverage report

### Build and Deploy Job

Runs on pushes to the main branch:
- Checks out code
- Sets up AWS credentials using OIDC
- Logs in to Amazon ECR
- Builds and tags the Docker image
- Pushes the image to ECR
- Downloads the current ECS task definition
- Updates the task definition with the new image
- Deploys the updated task definition to ECS
- Verifies the deployment
- Creates a deployment tag in git
- Generates a deployment summary

### Notification Job

(Optional) Sends a Slack notification with deployment status:
- Includes repository, branch, and commit details
- Shows success or failure status
- Links to the GitHub workflow run

## Triggering the Workflow

The workflow runs automatically on:
- Pull request to main (runs tests only)
- Push to main (runs full CI/CD pipeline)
- Manual trigger via GitHub UI

## Workflow Details

### Docker Build Process

- The workflow uses Docker BuildX for efficient builds
- Docker layer caching improves build speed
- Build arguments pass GitHub metadata to the container
- The container includes health checks and build information

### ECS Deployment

- The workflow downloads the current task definition
- It updates only the image, preserving all other settings
- Deployment includes a stability check
- Post-deployment verification confirms tasks are running

### Security Considerations

- The workflow uses OIDC for short-lived credentials
- Role permissions follow the principle of least privilege
- No AWS credentials are stored in GitHub secrets

## Monitoring Deployments

You can monitor deployments in several ways:

1. GitHub Actions dashboard in your repository
2. Deployment tags in your git history
3. AWS ECS console
4. CloudWatch logs
5. Slack notifications (if configured)

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Verify your IAM role conditions match your repository
   - Check that the AWS region in the workflow matches your deployment

2. **Build Failures**:
   - Check your Dockerfile for errors
   - Verify all dependencies are available

3. **Deployment Failures**:
   - Check if the task definition is valid
   - Look for errors in CloudWatch logs
   - Verify service stability in ECS console

### Debugging the Workflow

You can add additional debugging:

```yaml
- name: Debug environment
  run: |
    echo "GitHub SHA: ${{ github.sha }}"
    echo "GitHub REF: ${{ github.ref }}"
    echo "AWS Region: ${{ env.AWS_REGION }}"
    aws sts get-caller-identity
```

## Best Practices

1. **Branch Protection**:
   - Enable branch protection for main
   - Require status checks to pass before merging
   - Require pull request reviews

2. **Semantic Versioning**:
   - Consider using GitHub releases or tags for version tracking
   - Automate CHANGELOG generation

3. **Infrastructure as Code**:
   - Keep CloudFormation templates in version control
   - Consider automated infrastructure updates for major changes

4. **Secret Rotation**:
   - Periodically review and update IAM policies
   - Rotate Slack webhook URLs if needed

## Next Steps

Consider these enhancements to your CI/CD pipeline:

1. **Multi-environment deployments**:
   - Add staging and development environments
   - Use different AWS roles per environment

2. **Automated testing improvements**:
   - Add integration tests
   - Implement security scanning with tools like Trivy

3. **Rollback capability**:
   - Add automated rollback on deployment failure
   - Implement blue/green deployments

4. **Approval workflows**:
   - Add approval steps for production deployments
   - Implement change management integration