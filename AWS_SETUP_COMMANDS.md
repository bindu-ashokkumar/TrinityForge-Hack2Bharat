# AWS Setup Commands for Windows PowerShell

## Important: Use these commands in PowerShell (not Command Prompt)

### 1. Create S3 Bucket

```powershell
aws s3 mb s3://swasthcart-products --region us-east-1
```

### 2. Enable S3 Encryption (PowerShell version)

```powershell
$encryptionConfig = @"
{
  "Rules": [
    {
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }
  ]
}
"@

aws s3api put-bucket-encryption --bucket swasthcart-products --server-side-encryption-configuration $encryptionConfig
```

**OR use this single-line version:**

```powershell
aws s3api put-bucket-encryption --bucket swasthcart-products --server-side-encryption-configuration '{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"AES256\"}}]}'
```

### 3. Verify Bucket Creation

```powershell
aws s3 ls
```

### 4. Create DynamoDB Table

```powershell
aws dynamodb create-table --table-name swasthcart_sessions --attribute-definitions AttributeName=session_id,AttributeType=S --key-schema AttributeName=session_id,KeyType=HASH --billing-mode PAY_PER_REQUEST --region us-east-1
```

### 5. Enable DynamoDB TTL

```powershell
aws dynamodb update-time-to-live --table-name swasthcart_sessions --time-to-live-specification "Enabled=true,AttributeName=ttl"
```

### 6. Verify DynamoDB Table

```powershell
aws dynamodb describe-table --table-name swasthcart_sessions
```

### 7. Create CloudWatch Log Group

```powershell
aws logs create-log-group --log-group-name /aws/swasthcart
```

### 8. Verify Log Group

```powershell
aws logs describe-log-groups --log-group-name-prefix /aws/swasthcart
```

### 9. Get OpenSearch Endpoint (after creating domain in Console)

```powershell
aws opensearch describe-domain --domain-name swasthcart-guidelines --query 'DomainStatus.Endpoint' --output text
```

### 10. Get Your AWS Account ID

```powershell
aws sts get-caller-identity --query Account --output text
```

## Alternative: Use AWS Console

If PowerShell commands are giving issues, you can create resources via AWS Console:

1. **S3**: https://s3.console.aws.amazon.com/
2. **DynamoDB**: https://console.aws.amazon.com/dynamodb/
3. **OpenSearch**: https://console.aws.amazon.com/aos/
4. **Bedrock**: https://console.aws.amazon.com/bedrock/
5. **CloudWatch**: https://console.aws.amazon.com/cloudwatch/

## Quick Setup Script

Save this as `setup-aws.ps1` and run in PowerShell:

```powershell
# Create S3 bucket
Write-Host "Creating S3 bucket..." -ForegroundColor Green
aws s3 mb s3://swasthcart-products --region us-east-1

# Create DynamoDB table
Write-Host "Creating DynamoDB table..." -ForegroundColor Green
aws dynamodb create-table `
  --table-name swasthcart_sessions `
  --attribute-definitions AttributeName=session_id,AttributeType=S `
  --key-schema AttributeName=session_id,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST `
  --region us-east-1

# Enable TTL
Write-Host "Enabling DynamoDB TTL..." -ForegroundColor Green
aws dynamodb update-time-to-live `
  --table-name swasthcart_sessions `
  --time-to-live-specification "Enabled=true,AttributeName=ttl"

# Create CloudWatch log group
Write-Host "Creating CloudWatch log group..." -ForegroundColor Green
aws logs create-log-group --log-group-name /aws/swasthcart

Write-Host "AWS resources created successfully!" -ForegroundColor Green
Write-Host "Next: Create OpenSearch domain in AWS Console" -ForegroundColor Yellow
```

Run it:
```powershell
.\setup-aws.ps1
```
