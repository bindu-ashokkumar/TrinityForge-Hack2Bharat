#!/bin/bash
# ============================================
# SwasthCart - Create App Runner Service via CLI
# ============================================
# Run this AFTER deploy-apprunner.sh has pushed the image to ECR
# ============================================

set -e

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="316956665748"
ECR_REPO_NAME="swasthcart"
APP_RUNNER_SERVICE_NAME="swasthcart"
IMAGE_TAG="latest"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}"

echo "=========================================="
echo " Creating IAM Roles for App Runner"
echo "=========================================="

# Step 1: Create ECR access role for App Runner
echo "[1/4] Creating ECR access role..."

# Trust policy for App Runner to pull from ECR
cat > /tmp/apprunner-ecr-trust.json << 'TRUST'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "build.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
TRUST

aws iam create-role \
  --role-name SwasthCartAppRunnerECRRole \
  --assume-role-policy-document file:///tmp/apprunner-ecr-trust.json \
  --region ${AWS_REGION} 2>/dev/null || echo "  (Role already exists)"

aws iam attach-role-policy \
  --role-name SwasthCartAppRunnerECRRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess 2>/dev/null || true

# Step 2: Create instance role for the app (Bedrock, DynamoDB, S3, CloudWatch)
echo "[2/4] Creating instance role..."

cat > /tmp/apprunner-instance-trust.json << 'TRUST'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "tasks.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
TRUST

aws iam create-role \
  --role-name SwasthCartAppRunnerInstanceRole \
  --assume-role-policy-document file:///tmp/apprunner-instance-trust.json \
  --region ${AWS_REGION} 2>/dev/null || echo "  (Role already exists)"

# Attach policies for AWS services the app needs
for POLICY in \
  "arn:aws:iam::aws:policy/AmazonBedrockFullAccess" \
  "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess" \
  "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess" \
  "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"; do
  aws iam attach-role-policy \
    --role-name SwasthCartAppRunnerInstanceRole \
    --policy-arn ${POLICY} 2>/dev/null || true
done

echo "  Waiting 10s for IAM roles to propagate..."
sleep 10

# Step 3: Get role ARNs
ECR_ROLE_ARN=$(aws iam get-role --role-name SwasthCartAppRunnerECRRole --query 'Role.Arn' --output text)
INSTANCE_ROLE_ARN=$(aws iam get-role --role-name SwasthCartAppRunnerInstanceRole --query 'Role.Arn' --output text)

echo "  ECR Role: ${ECR_ROLE_ARN}"
echo "  Instance Role: ${INSTANCE_ROLE_ARN}"

# Step 4: Create App Runner service
echo "[3/4] Creating App Runner service..."

aws apprunner create-service \
  --service-name ${APP_RUNNER_SERVICE_NAME} \
  --source-configuration "{
    \"AuthenticationConfiguration\": {
      \"AccessRoleArn\": \"${ECR_ROLE_ARN}\"
    },
    \"AutoDeploymentsEnabled\": false,
    \"ImageRepository\": {
      \"ImageIdentifier\": \"${ECR_URI}\",
      \"ImageRepositoryType\": \"ECR\",
      \"ImageConfiguration\": {
        \"Port\": \"8501\",
        \"RuntimeEnvironmentVariables\": {
          \"AWS_DEFAULT_REGION\": \"${AWS_REGION}\"
        }
      }
    }
  }" \
  --instance-configuration "{
    \"Cpu\": \"1 vCPU\",
    \"Memory\": \"2 GB\",
    \"InstanceRoleArn\": \"${INSTANCE_ROLE_ARN}\"
  }" \
  --health-check-configuration "{
    \"Protocol\": \"HTTP\",
    \"Path\": \"/_stcore/health\",
    \"Interval\": 10,
    \"Timeout\": 5,
    \"HealthyThreshold\": 1,
    \"UnhealthyThreshold\": 5
  }" \
  --region ${AWS_REGION}

echo ""
echo "[4/4] Service creation initiated!"
echo ""
echo "=========================================="
echo " Checking deployment status..."
echo "=========================================="

# Wait and get the service URL
sleep 5
SERVICE_URL=$(aws apprunner describe-service \
  --service-arn $(aws apprunner list-services --region ${AWS_REGION} --query "ServiceSummaryList[?ServiceName=='${APP_RUNNER_SERVICE_NAME}'].ServiceArn" --output text) \
  --region ${AWS_REGION} \
  --query 'Service.ServiceUrl' --output text 2>/dev/null)

echo ""
echo "Service is deploying... (takes 3-5 minutes)"
echo ""
echo "Your public URL will be:"
echo "  https://${SERVICE_URL}"
echo ""
echo "Check status with:"
echo "  aws apprunner list-services --region ${AWS_REGION}"
echo ""
echo "=========================================="
