# Setting Up IAM for GitHub Actions

This document explains how to set up AWS IAM to work with GitHub Actions for the PolicyEdgeAI project.

## Step 1: Create an OpenID Connect (OIDC) Provider

1. Sign in to the AWS Management Console
2. Navigate to IAM → Identity providers → Add provider
3. Select "OpenID Connect"
4. For the Provider URL, enter: `https://token.actions.githubusercontent.com`
5. For the Audience, enter: `sts.amazonaws.com`
6. Verify the provider information and click "Add provider"

## Step 2: Create an IAM Role for GitHub Actions

1. Navigate to IAM → Roles → Create role
2. Select "Web identity" as the trusted entity
3. Select the Identity provider you just created: `token.actions.githubusercontent.com`
4. For Audience, select `sts.amazonaws.com`
5. Click "Next: Permissions"

6. Attach the following policies:
   - AmazonECR-FullAccess
   - AmazonS3FullAccess
   - SecretsManagerReadWrite

   If you want to enable full deployment, also add:
   - AmazonECS-FullAccess
   - AmazonEC2FullAccess
   - CloudFormationFullAccess
   - IAMFullAccess

7. Click "Next: Tags" (add any tags if needed)
8. Click "Next: Review"

9. Enter a name for the role: `GitHub-PolicyEdgeAI-Role`
10. Click "Create role"

## Step 3: Update the Trust Relationship

1. Navigate to IAM → Roles
2. Find and click on the role you just created
3. Click on the "Trust relationships" tab
4. Click "Edit trust policy"
5. Replace the policy with the following:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::904233121564:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:christina-ml/policyedgeai:*"
        }
      }
    }
  ]
}
```

6. Click "Update policy"

## Step 4: Get the Role ARN for GitHub Actions

1. After creating the role, go to the role's summary page
2. Find and copy the "Role ARN" (it should look like `arn:aws:iam::904233121564:role/GitHub-PolicyEdgeAI-Role`)
3. This ARN will be used in the GitHub Actions workflow as the `AWS_ROLE_ARN` secret

## Step 5: Add the Role ARN as a GitHub Secret

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `AWS_ROLE_ARN`
5. Value: The Role ARN you copied in Step 4
6. Click "Add secret"

## Additional Secrets to Add

Also add these secrets to your GitHub repository:

1. OPENAI_API_KEY: Your OpenAI API key
2. ANTHROPIC_API_KEY: Your Anthropic API key (if using Claude)
3. JWT_SECRET_KEY: A secure random string for JWT token signing