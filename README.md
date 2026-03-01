# SwasthCart AI - Streamlit MVP

Preventive Health Grocery Intelligence Platform

## Overview

SwasthCart AI provides personalized health risk assessments for grocery products using AWS Bedrock AI and RAG-grounded explanations. Built with Streamlit for rapid deployment.

## Features

- 🛒 Amazon Fresh-like product grid
- 🩺 Swasth Mode toggle for health intelligence
- 🎯 AI-powered risk scoring (🟢 Safe, 🟡 Moderate, 🔴 High Risk)
- 📊 Real-time cart health scoring
- 📚 RAG explanations with citations from WHO, FDA, AHA
- 👤 Individual and Family health profiles

## Tech Stack

- **Frontend**: Streamlit
- **AI**: Amazon Bedrock (Claude 3)
- **Vector DB**: Amazon OpenSearch
- **Storage**: S3, DynamoDB
- **Monitoring**: CloudWatch

## Quick Start

### Prerequisites

- Python 3.9+
- AWS Account with CLI configured
- AWS Services: S3, DynamoDB, Bedrock, OpenSearch

### Setup (5 minutes)

1. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure AWS** (edit `config/config.yaml`)
   ```yaml
   aws:
     region: us-east-1
     s3:
       bucket_name: your-bucket-name
     dynamodb:
       table_name: swasthcart_sessions
     opensearch:
       endpoint: https://your-opensearch-endpoint
   ```

3. **Generate and upload data**
   ```bash
   python scripts/generate_products.py
   aws s3 cp data/products.json s3://your-bucket-name/products.json
   python scripts/init_guidelines.py
   ```

4. **Run application**
   ```bash
   streamlit run app.py
   ```

5. **Open browser**: `http://localhost:8501`

## Complete Setup Guide

See **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for detailed AWS service configuration including:
- Step-by-step AWS resource setup
- IAM permissions configuration
- Troubleshooting common issues
- Cost estimates

## Project Structure

```
swasthcart-streamlit-mvp/
├── src/
│   ├── data_layer/          # AWS clients (S3, DynamoDB, Bedrock, OpenSearch)
│   ├── business_logic/      # Risk scoring, cart intelligence, RAG engine
│   ├── ui/                  # Streamlit UI components
│   └── models.py            # Data models
├── scripts/                 # Data generation scripts
├── deployment/              # Deployment configs (systemd, nginx, IAM)
├── config/                  # Application configuration
├── app.py                   # Main application
├── SETUP_GUIDE.md          # Complete AWS setup guide
└── README.md               # This file
```

## AWS Resources Required

1. **S3 Bucket** - Product data storage (~$1/month)
2. **DynamoDB Table** - Session storage (~$5/month)
3. **OpenSearch Domain** - Vector database (~$25/month)
4. **Bedrock Access** - Claude 3 + Titan Embeddings (~$10/month)
5. **CloudWatch** - Logging (~$1/month)

**Total Cost**: ~$40-50/month for demo

## Deployment

For production deployment on AWS EC2 with HTTPS:

```bash
# Copy deployment files
sudo cp deployment/swasthcart.service /etc/systemd/system/
sudo cp deployment/nginx.conf /etc/nginx/sites-available/swasthcart

# Start services
sudo systemctl enable swasthcart
sudo systemctl start swasthcart
sudo systemctl restart nginx

# Setup HTTPS
sudo certbot --nginx -d your-domain.com
```

## Troubleshooting

**AWS Credentials Error**
```bash
aws configure  # Enter your AWS credentials
```

**Bedrock Access Denied**
- Go to AWS Console → Bedrock → Model access
- Request access to Claude 3 and Titan models

**OpenSearch Connection Failed**
- Verify endpoint in config.yaml
- Check domain is "Active" in AWS Console

See **SETUP_GUIDE.md** for detailed troubleshooting.

## Security

- IAM roles for AWS access (no hardcoded credentials)
- KMS encryption for data at rest
- HTTPS with Let's Encrypt
- Session auto-deletion (2-hour TTL)
- No PHI storage

## License

Proprietary

---

**⚠️ Disclaimer**: This tool provides informational guidance only and is not medical advice.
