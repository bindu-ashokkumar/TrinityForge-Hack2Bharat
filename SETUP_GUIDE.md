# SwasthCart AI - Complete Setup Guide

Step-by-step guide to set up all AWS services and run the application.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [AWS Services Configuration](#aws-services-configuration)
4. [Local Development Setup](#local-development-setup)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Python 3.9 or higher
- pip (Python package manager)
- AWS CLI installed and configured
- Git (for cloning repository)

### AWS Account Requirements
- Active AWS account
- Credit card on file (for AWS services)
- Basic understanding of AWS Console

### Estimated Costs
- **Development/Testing**: $5-10/month
- **Demo/Hackathon**: $70-100/month
- **Production**: $200-500/month (depending on usage)

---

## AWS Account Setup

### Step 1: Create AWS Account

1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Follow the registration process
4. Add payment method
5. Verify your identity

### Step 2: Install AWS CLI

**On Windows:**
```bash
# Download and run the AWS CLI MSI installer
# https://awscli.amazonaws.com/AWSCLIV2.msi
```

**On macOS:**
```bash
brew install awscli
```

**On Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Step 3: Configure AWS CLI

```bash
aws configure
```

Enter your credentials:
- **AWS Access Key ID**: [Your access key]
- **AWS Secret Access Key**: [Your secret key]
- **Default region name**: us-east-1
- **Default output format**: json

**To get your access keys:**
1. Go to AWS Console → IAM
2. Click on your username
3. Go to "Security credentials" tab
4. Click "Create access key"
5. Download and save the credentials

---

## AWS Services Configuration

### Service 1: Amazon S3 (Product Data Storage)

**Purpose**: Store synthetic product dataset

**Setup Steps:**

1. **Create S3 Bucket**
   ```bash
   aws s3 mb s3://swasthcart-products-[YOUR-NAME] --region us-east-1
   ```
   
   Replace `[YOUR-NAME]` with something unique (e.g., your name or random string)

2. **Enable Encryption**
   ```bash
   aws s3api put-bucket-encryption \
     --bucket swasthcart-products-[YOUR-NAME] \
     --server-side-encryption-configuration '{
       "Rules": [{
         "ApplyServerSideEncryptionByDefault": {
           "SSEAlgorithm": "AES256"
         }
       }]
     }'
   ```

3. **Verify Bucket Creation**
   ```bash
   aws s3 ls
   ```

**Cost**: ~$0.023 per GB/month (minimal for demo)

---

### Service 2: Amazon DynamoDB (Session Storage)

**Purpose**: Store user sessions and cart data

**Setup Steps:**

1. **Create DynamoDB Table**
   ```bash
   aws dynamodb create-table \
     --table-name swasthcart_sessions \
     --attribute-definitions AttributeName=session_id,AttributeType=S \
     --key-schema AttributeName=session_id,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST \
     --region us-east-1
   ```

2. **Enable TTL (Time To Live)**
   ```bash
   aws dynamodb update-time-to-live \
     --table-name swasthcart_sessions \
     --time-to-live-specification "Enabled=true, AttributeName=ttl"
   ```

3. **Verify Table Creation**
   ```bash
   aws dynamodb describe-table --table-name swasthcart_sessions
   ```

**Cost**: Pay-per-request (minimal for demo, ~$1-5/month)

---

### Service 3: Amazon Bedrock (AI Reasoning)

**Purpose**: AI-powered risk scoring and explanation generation

**Setup Steps:**

✅ **No setup required!** Bedrock models are now automatically enabled when first invoked.

**What happens:**
- Models activate automatically on first use
- For Anthropic Claude models, you may need to submit use case details on first invocation
- The application will handle this automatically

**Verify Bedrock is available** (optional):
```bash
aws bedrock list-foundation-models --region us-east-1
```

**Models used by this app:**
- **Claude 3 Sonnet** - Risk scoring and explanations
- **Claude 3 Haiku** - Fast ingredient analysis
- **Titan Embeddings** - Vector embeddings for RAG

**Cost**: Pay-per-use
- Claude 3 Sonnet: ~$3 per 1M input tokens
- Titan Embeddings: ~$0.10 per 1M tokens
- Estimated demo cost: $5-10/month

---

### Service 4: Amazon OpenSearch (Vector Database)

**Purpose**: Store and search health guideline embeddings

**Setup Steps:**

1. **Go to AWS Console**
   - Navigate to Amazon OpenSearch Service
   - Or visit: https://console.aws.amazon.com/aos/

2. **Create Domain**
   - Click "Create domain"
   - **Domain name**: `swasthcart-guidelines`
   - **Deployment type**: Development and testing
   - **Version**: Latest (e.g., OpenSearch 2.11)
   - **Instance type**: `t3.small.search` (cheapest option)
   - **Number of nodes**: 1
   - **EBS storage**: 10 GB (gp3)
   - **Network**: Public access (for demo)
   - **Fine-grained access control**: Enable
     - Create master user
     - Username: `admin`
     - Password: [Create strong password]
   - **Access policy**: Allow open access (for demo only)
   - Click "Create"

3. **Wait for Domain Creation** (10-15 minutes)
   - Status will change from "Loading" to "Active"

4. **Get Domain Endpoint**
   ```bash
   aws opensearch describe-domain --domain-name swasthcart-guidelines --query 'DomainStatus.Endpoint' --output text
   ```
   
   Save this endpoint - you'll need it for configuration!

**Cost**: ~$25-30/month for t3.small.search

**Important**: For production, use VPC access instead of public access!

---

### Service 5: Amazon CloudWatch (Logging)

**Purpose**: Application logging and monitoring

**Setup Steps:**

1. **Create Log Group**
   ```bash
   aws logs create-log-group --log-group-name /aws/swasthcart
   ```

2. **Verify Log Group**
   ```bash
   aws logs describe-log-groups --log-group-name-prefix /aws/swasthcart
   ```

**Cost**: $0.50 per GB ingested (minimal for demo)

---

### Service 6: IAM Role (Permissions)

**Purpose**: Grant application access to AWS services

**Setup Steps:**

1. **Create IAM Policy**
   
   Save this as `swasthcart-policy.json`:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": ["s3:GetObject", "s3:ListBucket"],
         "Resource": [
           "arn:aws:s3:::swasthcart-products-[YOUR-NAME]",
           "arn:aws:s3:::swasthcart-products-[YOUR-NAME]/*"
         ]
       },
       {
         "Effect": "Allow",
         "Action": ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem"],
         "Resource": "arn:aws:dynamodb:us-east-1:*:table/swasthcart_sessions"
       },
       {
         "Effect": "Allow",
         "Action": ["bedrock:InvokeModel"],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": ["es:ESHttpGet", "es:ESHttpPost", "es:ESHttpPut"],
         "Resource": "arn:aws:es:us-east-1:*:domain/swasthcart-guidelines/*"
       },
       {
         "Effect": "Allow",
         "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
         "Resource": "arn:aws:logs:us-east-1:*:log-group:/aws/swasthcart:*"
       }
     ]
   }
   ```

2. **Create Policy**
   ```bash
   aws iam create-policy \
     --policy-name SwasthCartPolicy \
     --policy-document file://swasthcart-policy.json
   ```

3. **Attach Policy to Your User** (for local development)
   ```bash
   aws iam attach-user-policy \
     --user-name [YOUR-IAM-USERNAME] \
     --policy-arn arn:aws:iam::[YOUR-ACCOUNT-ID]:policy/SwasthCartPolicy
   ```

**To find your account ID:**
```bash
aws sts get-caller-identity --query Account --output text
```

---

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone <your-repo-url>
cd swasthcart-streamlit-mvp
```

### Step 2: Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Application

Edit `config/config.yaml`:

```yaml
aws:
  region: us-east-1
  s3:
    bucket_name: swasthcart-products-[YOUR-NAME]  # Replace with your bucket name
    products_key: products.json
  dynamodb:
    table_name: swasthcart_sessions
  bedrock:
    model_id: anthropic.claude-3-sonnet-20240229-v1:0
    embedding_model_id: amazon.titan-embed-text-v1
    timeout: 5
  opensearch:
    endpoint: https://[YOUR-OPENSEARCH-ENDPOINT]  # Replace with your endpoint
    index_name: health_guidelines
  cloudwatch:
    log_group: /aws/swasthcart

app:
  session_ttl_hours: 2
  max_products_display: 100
  cart_improvement_threshold: 60
```

**Important**: Replace the placeholders:
- `[YOUR-NAME]` with your S3 bucket suffix
- `[YOUR-OPENSEARCH-ENDPOINT]` with your OpenSearch domain endpoint

### Step 5: Generate Synthetic Data

```bash
python scripts/generate_products.py
```

This creates `data/products.json` with 100 synthetic products.

### Step 6: Upload Data to S3

```bash
aws s3 cp data/products.json s3://swasthcart-products-[YOUR-NAME]/products.json
```

Verify upload:
```bash
aws s3 ls s3://swasthcart-products-[YOUR-NAME]/
```

### Step 7: Initialize Health Guidelines

```bash
python scripts/init_guidelines.py
```

This will:
1. Create OpenSearch index
2. Generate embeddings for 20 health guidelines
3. Index them in OpenSearch

**Expected output:**
```
Initializing health guidelines in OpenSearch...
Connecting to AWS services...
Creating OpenSearch index...
Created index health_guidelines
Indexing 20 guidelines...
✅ Indexed: guideline_001
✅ Indexed: guideline_002
...
✅ Successfully indexed 20/20 guidelines
```

---

## Running the Application

### Start the Application

```bash
streamlit run app.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.x:8501
```

### Access the Application

Open your browser and go to: **http://localhost:8501**

### First-Time Setup in UI

1. **Toggle Swasth Mode ON** (top right)
2. **Expand Health Profile** section
3. **Select health conditions** (e.g., Diabetes, Hypertension)
4. **Browse products** - you'll see risk badges (🟢🟡🔴)
5. **Add products to cart** - watch cart health score update
6. **Click "Why this score?"** - see AI-generated explanations with citations

---

## Troubleshooting

### Issue 1: AWS Credentials Not Found

**Error**: `Unable to locate credentials`

**Solution**:
```bash
# Verify AWS CLI is configured
aws sts get-caller-identity

# If not configured, run:
aws configure
```

---

### Issue 2: Bedrock Access Denied

**Error**: `AccessDeniedException: Could not access model`

**Solution**:
1. **For Anthropic Claude models**: On first use, you may need to submit use case details
   - Go to AWS Console → Bedrock
   - Try invoking the model - you'll be prompted for use case info
   - Fill in the form (takes 1-2 minutes)
   - Models will be enabled immediately after submission

2. **Verify IAM permissions**: Ensure your IAM user/role has `bedrock:InvokeModel` permission

3. **Check region**: Bedrock must be used in supported regions (us-east-1, us-west-2, etc.)

---

### Issue 3: OpenSearch Connection Failed

**Error**: `ConnectionError: Unable to connect to OpenSearch`

**Solution**:
1. Verify OpenSearch domain is "Active":
   ```bash
   aws opensearch describe-domain --domain-name swasthcart-guidelines
   ```
2. Check endpoint in `config/config.yaml` matches domain endpoint
3. Verify security group allows your IP (if using VPC)
4. For public access, ensure access policy allows connections

---

### Issue 4: S3 Access Denied

**Error**: `AccessDenied: Access Denied`

**Solution**:
1. Verify bucket name in `config/config.yaml` is correct
2. Check IAM policy includes S3 permissions
3. Verify products.json was uploaded:
   ```bash
   aws s3 ls s3://swasthcart-products-[YOUR-NAME]/
   ```

---

### Issue 5: DynamoDB Table Not Found

**Error**: `ResourceNotFoundException: Table not found`

**Solution**:
```bash
# Verify table exists
aws dynamodb describe-table --table-name swasthcart_sessions

# If not, create it:
aws dynamodb create-table \
  --table-name swasthcart_sessions \
  --attribute-definitions AttributeName=session_id,AttributeType=S \
  --key-schema AttributeName=session_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

---

### Issue 6: Python Dependencies Error

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Issue 7: OpenSearch Index Creation Failed

**Error**: `AuthenticationException` or `RequestError`

**Solution**:
1. Verify OpenSearch domain has fine-grained access control enabled
2. Update `opensearch_client.py` to use master username/password if needed
3. Or disable fine-grained access control (not recommended for production)

---

## Verification Checklist

Before running the application, verify:

- [ ] AWS CLI is installed and configured
- [ ] S3 bucket created and products.json uploaded
- [ ] DynamoDB table created with TTL enabled
- [ ] Bedrock model access granted (Claude 3 + Titan)
- [ ] OpenSearch domain is Active
- [ ] CloudWatch log group created
- [ ] IAM permissions configured
- [ ] config/config.yaml updated with your resource names
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Health guidelines indexed in OpenSearch

---

## Quick Start Commands (Summary)

```bash
# 1. Configure AWS
aws configure

# 2. Create AWS resources
aws s3 mb s3://swasthcart-products-demo
aws dynamodb create-table --table-name swasthcart_sessions --attribute-definitions AttributeName=session_id,AttributeType=S --key-schema AttributeName=session_id,KeyType=HASH --billing-mode PAY_PER_REQUEST
aws logs create-log-group --log-group-name /aws/swasthcart

# 3. Setup application
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 4. Generate and upload data
python scripts/generate_products.py
aws s3 cp data/products.json s3://swasthcart-products-demo/products.json

# 5. Initialize guidelines (after configuring OpenSearch in config.yaml)
python scripts/init_guidelines.py

# 6. Run application
streamlit run app.py
```

---

## Cost Management Tips

### For Development/Testing:
1. Use smallest instance types (t3.small)
2. Delete resources when not in use
3. Use DynamoDB on-demand billing
4. Set up billing alerts in AWS Console

### To Delete All Resources:
```bash
# Delete S3 bucket
aws s3 rb s3://swasthcart-products-[YOUR-NAME] --force

# Delete DynamoDB table
aws dynamodb delete-table --table-name swasthcart_sessions

# Delete OpenSearch domain (via Console - takes 10-15 minutes)

# Delete CloudWatch log group
aws logs delete-log-group --log-group-name /aws/swasthcart
```

---

## Next Steps

1. **Test the application** - Add products to cart, view explanations
2. **Review logs** - Check CloudWatch for application logs
3. **Deploy to EC2** - Follow `docs/DEPLOYMENT.md` for production deployment
4. **Customize** - Modify products, add more guidelines, adjust risk thresholds

---

## Support

For issues:
1. Check this troubleshooting section
2. Review CloudWatch logs for errors
3. Verify all AWS resources are properly configured
4. Check `docs/DEPLOYMENT.md` for additional guidance

---

## Important Notes

⚠️ **Security**: This setup uses public access for OpenSearch (demo only). For production, use VPC access.

⚠️ **Costs**: Monitor your AWS billing dashboard regularly. Set up billing alerts.

⚠️ **Credentials**: Never commit AWS credentials to Git. Use IAM roles for EC2 deployment.

⚠️ **Disclaimer**: This tool provides informational guidance only and is not medical advice.

---

**Ready to start?** Follow the steps above and you'll have SwasthCart AI running in 30-45 minutes! 🚀
