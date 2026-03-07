#!/bin/bash
# ============================================
# SwasthCart - AWS App Runner Deployment Script
# ============================================
# Prerequisites:
#   - AWS CLI configured with appropriate permissions
#   - Docker installed and running
#   - Run this script from the project root directory
# ============================================

set -e

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="316956665748"
ECR_REPO_NAME="swasthcart"
APP_RUNNER_SERVICE_NAME="swasthcart"
IMAGE_TAG="latest"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "=========================================="
echo " SwasthCart - App Runner Deployment"
echo "=========================================="

# Step 1: Create ECR Repository (if not exists)
echo ""
echo "[1/5] Creating ECR repository..."
aws ecr describe-repositories --repository-names ${ECR_REPO_NAME} --region ${AWS_REGION} 2>/dev/null || \
aws ecr create-repository --repository-name ${ECR_REPO_NAME} --region ${AWS_REGION} --image-scanning-configuration scanOnPush=true

# Step 2: Login to ECR
echo ""
echo "[2/5] Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Step 3: Build Docker image
echo ""
echo "[3/5] Building Docker image..."
docker build -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

# Step 4: Tag and push to ECR
echo ""
echo "[4/5] Pushing image to ECR..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}
docker push ${ECR_URI}:${IMAGE_TAG}

echo ""
echo "[5/5] Image pushed successfully!"
echo ""
echo "ECR Image URI: ${ECR_URI}:${IMAGE_TAG}"
echo ""
echo "=========================================="
echo " NEXT: Create App Runner Service"
echo "=========================================="
echo ""
echo "Option A: Use AWS Console (Recommended for first time)"
echo "  1. Go to: https://us-east-1.console.aws.amazon.com/apprunner"
echo "  2. Click 'Create service'"
echo "  3. Source: Container registry > Amazon ECR"
echo "  4. Image URI: ${ECR_URI}:${IMAGE_TAG}"
echo "  5. Deployment: Manual (or Automatic)"
echo "  6. ECR access role: Create new role (AppRunnerECRAccessRole)"
echo "  7. Service name: ${APP_RUNNER_SERVICE_NAME}"
echo "  8. Port: 8501"
echo "  9. CPU: 1 vCPU, Memory: 2 GB"
echo " 10. Add environment variables (from .env file if needed)"
echo " 11. Instance role: Select role with Bedrock/DynamoDB/S3/CloudWatch access"
echo " 12. Click 'Create & deploy'"
echo ""
echo "Option B: Use CLI (run deploy-apprunner-service.sh after this)"
echo ""
echo "=========================================="
