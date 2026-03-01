# SwasthCart AI - Public Deployment Guide

Make your SwasthCart AI app accessible via public URL using Streamlit Community Cloud (FREE) or AWS EC2.

---

## Option 1: Streamlit Community Cloud (Recommended - FREE & Easy)

### Prerequisites
- GitHub account
- Your code pushed to a GitHub repository

### Steps:

1. **Push Code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - SwasthCart AI"
   git remote add origin https://github.com/YOUR_USERNAME/swasthcart-ai.git
   git push -u origin main
   ```

2. **Create Streamlit Secrets File**
   
   Create `.streamlit/secrets.toml` in your repo:
   ```toml
   [aws]
   AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY"
   AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_KEY"
   AWS_DEFAULT_REGION = "ap-south-2"
   ```
   
   **IMPORTANT:** Add `.streamlit/secrets.toml` to `.gitignore` to avoid committing credentials!

3. **Update Code to Use Secrets**
   
   Modify AWS client initialization to use Streamlit secrets in production:
   ```python
   import streamlit as st
   import boto3
   
   # Check if running on Streamlit Cloud
   if hasattr(st, 'secrets') and 'aws' in st.secrets:
       # Use Streamlit secrets
       session = boto3.Session(
           aws_access_key_id=st.secrets['aws']['AWS_ACCESS_KEY_ID'],
           aws_secret_access_key=st.secrets['aws']['AWS_SECRET_ACCESS_KEY'],
           region_name=st.secrets['aws']['AWS_DEFAULT_REGION']
       )
   else:
       # Use local AWS credentials
       session = boto3.Session()
   ```

4. **Deploy to Streamlit Cloud**
   
   a. Go to https://share.streamlit.io/
   
   b. Sign in with GitHub
   
   c. Click "New app"
   
   d. Select your repository, branch (main), and main file (app.py)
   
   e. Click "Advanced settings" and add secrets:
      - Copy contents from `.streamlit/secrets.toml`
      - Paste into the secrets text area
   
   f. Click "Deploy"

5. **Get Your Public URL**
   
   Your app will be available at:
   ```
   https://YOUR_USERNAME-swasthcart-ai-app-RANDOM.streamlit.app
   ```

### Pros:
- ✅ FREE (unlimited public apps)
- ✅ Automatic HTTPS
- ✅ Auto-deploys on git push
- ✅ No server management
- ✅ Built-in secrets management

### Cons:
- ⚠️ Apps sleep after inactivity (wake up on first visit)
- ⚠️ Limited resources (1 GB RAM, 1 CPU)
- ⚠️ Public repository required (or paid plan)

---

## Option 2: AWS EC2 Deployment (Full Control)

### Prerequisites
- AWS account
- EC2 instance (t2.micro for testing, t2.medium for production)

### Steps:

1. **Launch EC2 Instance**
   ```bash
   # Use Amazon Linux 2 or Ubuntu 22.04
   # Security Group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS), 8501 (Streamlit)
   ```

2. **Connect to Instance**
   ```bash
   ssh -i your-key.pem ec2-user@YOUR_EC2_IP
   ```

3. **Install Dependencies**
   ```bash
   # Update system
   sudo yum update -y  # Amazon Linux
   # OR
   sudo apt update && sudo apt upgrade -y  # Ubuntu
   
   # Install Python 3.9+
   sudo yum install python3 python3-pip -y  # Amazon Linux
   # OR
   sudo apt install python3 python3-pip -y  # Ubuntu
   
   # Install Git
   sudo yum install git -y  # Amazon Linux
   # OR
   sudo apt install git -y  # Ubuntu
   ```

4. **Clone Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/swasthcart-ai.git
   cd swasthcart-ai
   ```

5. **Setup Application**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure AWS credentials
   aws configure
   ```

6. **Setup Systemd Service**
   
   Create `/etc/systemd/system/swasthcart.service`:
   ```ini
   [Unit]
   Description=SwasthCart AI Streamlit App
   After=network.target
   
   [Service]
   Type=simple
   User=ec2-user
   WorkingDirectory=/home/ec2-user/swasthcart-ai
   Environment="PATH=/home/ec2-user/swasthcart-ai/venv/bin"
   ExecStart=/home/ec2-user/swasthcart-ai/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable swasthcart
   sudo systemctl start swasthcart
   sudo systemctl status swasthcart
   ```

7. **Setup Nginx Reverse Proxy (Optional)**
   
   Install Nginx:
   ```bash
   sudo yum install nginx -y  # Amazon Linux
   # OR
   sudo apt install nginx -y  # Ubuntu
   ```
   
   Configure `/etc/nginx/conf.d/swasthcart.conf`:
   ```nginx
   server {
       listen 80;
       server_name YOUR_DOMAIN_OR_IP;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
   
   Start Nginx:
   ```bash
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

8. **Setup SSL with Let's Encrypt (Optional)**
   ```bash
   sudo yum install certbot python3-certbot-nginx -y  # Amazon Linux
   # OR
   sudo apt install certbot python3-certbot-nginx -y  # Ubuntu
   
   sudo certbot --nginx -d YOUR_DOMAIN
   ```

9. **Access Your App**
   ```
   http://YOUR_EC2_IP:8501
   # OR with Nginx
   http://YOUR_DOMAIN
   # OR with SSL
   https://YOUR_DOMAIN
   ```

### Pros:
- ✅ Full control over resources
- ✅ No sleep/wake delays
- ✅ Private repository support
- ✅ Custom domain support
- ✅ Scalable

### Cons:
- ⚠️ Costs money (~$10-50/month)
- ⚠️ Requires server management
- ⚠️ Manual SSL setup
- ⚠️ Manual deployments

---

## Option 3: Streamlit Cloud (Paid Plan)

### Features:
- Private repositories
- More resources (4 GB RAM, 2 CPUs)
- No sleep mode
- Priority support

### Pricing:
- $20/month per user

### Steps:
Same as Option 1, but with paid plan benefits.

---

## Recommended Approach for Hackathon/Demo:

**Use Streamlit Community Cloud (Option 1)**

Reasons:
1. FREE and fast to deploy
2. Automatic HTTPS and custom subdomain
3. Perfect for demos and hackathons
4. Easy to share with judges/users
5. No server management needed

---

## Security Best Practices:

1. **Never commit AWS credentials**
   - Use `.gitignore` for secrets
   - Use Streamlit secrets or environment variables

2. **Use IAM roles on EC2**
   - Attach IAM role to EC2 instance
   - No need to store credentials on server

3. **Restrict S3 bucket access**
   - Use bucket policies
   - Enable encryption

4. **Use HTTPS in production**
   - Let's Encrypt for free SSL
   - Or use CloudFront with S3

5. **Monitor costs**
   - Set up AWS billing alerts
   - Use AWS Cost Explorer

---

## Troubleshooting:

### Streamlit Cloud Issues:

**App won't start:**
- Check logs in Streamlit Cloud dashboard
- Verify secrets are configured correctly
- Check requirements.txt has all dependencies

**AWS connection fails:**
- Verify AWS credentials in secrets
- Check IAM permissions
- Verify region is correct

### EC2 Issues:

**Can't connect to app:**
- Check security group allows port 8501
- Verify app is running: `sudo systemctl status swasthcart`
- Check logs: `sudo journalctl -u swasthcart -f`

**App crashes:**
- Check memory usage: `free -h`
- Upgrade instance type if needed
- Check logs for errors

---

## Custom Domain Setup:

1. **Buy domain** (Namecheap, GoDaddy, etc.)

2. **For Streamlit Cloud:**
   - Go to app settings
   - Add custom domain
   - Update DNS CNAME record

3. **For EC2:**
   - Point A record to EC2 IP
   - Setup SSL with certbot

---

## Monitoring & Analytics:

1. **Streamlit Cloud:**
   - Built-in analytics dashboard
   - View app usage and errors

2. **EC2:**
   - Use CloudWatch for logs
   - Setup CloudWatch alarms
   - Use AWS X-Ray for tracing

---

## Cost Estimates:

### Streamlit Cloud (Free):
- $0/month

### Streamlit Cloud (Paid):
- $20/month per user

### AWS EC2:
- t2.micro (1 GB RAM): ~$8/month
- t2.small (2 GB RAM): ~$17/month
- t2.medium (4 GB RAM): ~$34/month
- + Data transfer costs
- + EBS storage costs

### AWS Services (for both):
- S3: ~$1/month
- DynamoDB: ~$1-5/month
- OpenSearch: ~$25-30/month
- Bedrock: ~$5-10/month (usage-based)
- CloudWatch: ~$1/month

**Total for Demo:** ~$40-50/month (with EC2) or ~$35-45/month (with Streamlit Cloud free)

---

## Next Steps:

1. Choose deployment option (Streamlit Cloud recommended)
2. Push code to GitHub
3. Setup secrets/credentials
4. Deploy and test
5. Share public URL with users/judges
6. Monitor usage and costs

---

**Ready to deploy?** Follow Option 1 for the fastest path to a public URL! 🚀
