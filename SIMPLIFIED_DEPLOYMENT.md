# Simplified Deployment Guide for PolicyEdgeAI

Since we have limited AWS permissions, here's a simplified deployment approach that will work with your current access level.

## 1. GitHub Actions for Docker Images

We've set up a GitHub Actions workflow (`build-images.yml`) that will build and push Docker images to ECR, which you have permission to use. To make this work:

1. Create a GitHub repository (e.g., `github.com/christina-ml/policyedgeai`)
2. Push your code to this repository:
   ```bash
   git remote add origin https://github.com/christina-ml/policyedgeai.git
   git push -u origin main
   ```
3. Have your AWS administrator set up the IAM role as described in `github_actions_iam_setup.md`
4. Add the following GitHub secrets:
   - AWS_ROLE_ARN: The ARN of the IAM role
   - OPENAI_API_KEY: Your OpenAI API key
   - ANTHROPIC_API_KEY: Your Anthropic API key

This workflow will build and push Docker images to your ECR repositories.

## 2. Manual Deployment (with limited permissions)

Once the images are in ECR, you can deploy manually:

### Option A: Use AWS ECS Console (if you gain ECS permissions)

1. Log in to AWS Console
2. Go to Amazon ECS → Task Definitions
3. Create a task definition:
   - Use the ECR images for policyedgeai-api and policyedgeai-dashboard
   - Set up port mappings (8000 for API, 8501 for dashboard)
   - Add environment variables from .env.example
4. Create an ECS cluster
5. Create services to run your task definitions

### Option B: EC2 Instance (if you gain EC2 permissions)

1. Launch an EC2 instance
2. Install Docker on the instance
3. Configure AWS credentials on the instance
4. Pull your images from ECR:
   ```bash
   aws ecr get-login-password | docker login --username AWS --password-stdin 904233121564.dkr.ecr.us-east-2.amazonaws.com
   docker pull 904233121564.dkr.ecr.us-east-2.amazonaws.com/policyedgeai-api:latest
   docker pull 904233121564.dkr.ecr.us-east-2.amazonaws.com/policyedgeai-dashboard:latest
   ```
5. Run the containers:
   ```bash
   docker run -d -p 8000:8000 --name api --env-file .env 904233121564.dkr.ecr.us-east-2.amazonaws.com/policyedgeai-api:latest
   docker run -d -p 8501:8501 --name dashboard --env-file .env 904233121564.dkr.ecr.us-east-2.amazonaws.com/policyedgeai-dashboard:latest
   ```

### Option C: Third-Party Cloud Service

If you can't get additional AWS permissions, consider:

1. **Heroku**: Deploy the Docker images directly from GitHub
2. **Digital Ocean App Platform**: Deploy from a GitHub repository
3. **Railway**: Simple deployment from GitHub with Docker support

## 3. Local Development

For testing on your local machine:

1. Install Docker Desktop
2. Build and run the containers locally:
   ```bash
   # Build API container
   docker build -t policyedgeai-api:local -f api.Dockerfile .
   
   # Build Dashboard container
   docker build -t policyedgeai-dashboard:local -f dashboard.Dockerfile .
   
   # Run containers
   docker run -d -p 8000:8000 --name api --env-file .env policyedgeai-api:local
   docker run -d -p 8501:8501 --name dashboard --env-file .env policyedgeai-dashboard:local
   ```
3. Access the applications at:
   - API: http://localhost:8000
   - Dashboard: http://localhost:8501

## Next Steps

1. Send the `aws_permissions_request.md` file to your AWS administrator requesting additional permissions
2. Follow the instructions in `github_actions_iam_setup.md` to set up IAM for GitHub Actions
3. Push your code to GitHub to trigger the workflow that builds and pushes Docker images
4. Select one of the deployment options based on your permissions