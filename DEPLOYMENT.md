# 🚀 Deployment Guide - CareerMatch AI

This guide covers deploying your Resume Screener application to various cloud platforms with CI/CD automation.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Cloud Deployment Options](#cloud-deployment-options)
   - [Railway (Recommended)](#option-1-railway-recommended)
   - [Render](#option-2-render)
   - [Docker Deployment](#option-3-docker-deployment)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Environment Variables](#environment-variables)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ Git installed and repository pushed to GitHub
- ✅ Python 3.11+ installed locally
- ✅ Docker installed (for containerized deployment)
- ✅ Cloud platform account (Railway/Render/etc.)

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Prachi5555/CareerMatch-AI.git
cd CareerMatch-AI
```

### 2. Create Environment File

Copy the example environment file and configure it:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=prachi
DB_PASSWORD=your_mysql_password
DB_NAME=resume_analyzer

# Application
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 4. Setup Database

```bash
python setup_mysql.py
```

### 5. Run Locally

```bash
streamlit run resume_chatbot.py
```

Visit: `http://localhost:8501`

---

## Cloud Deployment Options

### Option 1: Railway (Recommended) ⭐

**Why Railway?**
- ✅ Free tier with MySQL database
- ✅ Automatic deployments from GitHub
- ✅ Built-in environment variables management
- ✅ Easy scaling

#### Steps:

1. **Create Railway Account**
   - Visit [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `CareerMatch-AI` repository

3. **Add MySQL Database**
   - In your project, click "New"
   - Select "Database" → "MySQL"
   - Railway will automatically create the database

4. **Configure Environment Variables**
   
   Go to your app service → Variables tab and add:

   ```
   APP_ENV=production
   DEBUG=False
   SECRET_KEY=<generate-random-key>
   DB_HOST=${{MySQL.MYSQL_HOST}}
   DB_PORT=${{MySQL.MYSQL_PORT}}
   DB_USER=${{MySQL.MYSQL_USER}}
   DB_PASSWORD=${{MySQL.MYSQL_PASSWORD}}
   DB_NAME=${{MySQL.MYSQL_DATABASE}}
   ```

5. **Deploy**
   - Railway automatically deploys from `main` branch
   - Every push to `main` triggers auto-deployment
   - View logs in Railway dashboard

6. **Setup Database Schema**
   
   After first deployment, run setup:
   ```bash
   railway run python setup_mysql.py
   ```

---

### Option 2: Render

**Why Render?**
- ✅ Free tier available
- ✅ Auto-deploy from GitHub
- ✅ Managed PostgreSQL/MySQL

#### Steps:

1. **Create Render Account**
   - Visit [render.com](https://render.com)
   - Sign up with GitHub

2. **Deploy Using Blueprint**
   
   Your project includes `render.yaml` configuration:
   
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will read `render.yaml` and create:
     - Web service (your app)
     - MySQL database

3. **Environment Variables**
   
   Render automatically configures database variables from `render.yaml`
   
   Add additional variables in dashboard:
   ```
   SECRET_KEY=<generate-random-key>
   ```

4. **Deploy**
   - Render auto-deploys on every push to `main`
   - View deployment logs in dashboard

---

### Option 3: Docker Deployment

**For any cloud provider supporting Docker (AWS, Azure, GCP, DigitalOcean)**

#### Local Docker Testing:

```bash
# Build image
docker build -t resume-screener .

# Run with docker-compose (includes MySQL)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

#### Deploy to Cloud:

**AWS ECS/Fargate:**
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t resume-screener .
docker tag resume-screener:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/resume-screener:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/resume-screener:latest
```

**Azure Container Instances:**
```bash
az container create --resource-group myResourceGroup \
  --name resume-screener \
  --image resume-screener:latest \
  --dns-name-label resume-screener \
  --ports 8501
```

**Google Cloud Run:**
```bash
gcloud run deploy resume-screener \
  --image gcr.io/PROJECT_ID/resume-screener \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## CI/CD Pipeline

Your project includes automated GitHub Actions workflows:

### Workflow 1: CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`

**Jobs:**
1. **Test** - Code quality checks, linting, security scan
2. **Build** - Build Docker image
3. **Deploy** - Auto-deploy to Railway (on `main` branch)

### Workflow 2: Docker Build (`.github/workflows/docker-build.yml`)

**Triggers:**
- New release published
- Manual workflow dispatch

**Actions:**
- Builds multi-platform Docker images
- Pushes to Docker Hub

### Setup GitHub Secrets

For CI/CD to work, add these secrets in GitHub:

**Settings → Secrets and variables → Actions → New repository secret**

```
RAILWAY_TOKEN=<your-railway-token>
DOCKERHUB_USERNAME=<your-dockerhub-username>
DOCKERHUB_TOKEN=<your-dockerhub-token>
```

**Get Railway Token:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and get token
railway login
railway whoami
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | Database host | `localhost` or cloud host |
| `DB_PORT` | Database port | `3306` |
| `DB_USER` | Database username | `root` or `appuser` |
| `DB_PASSWORD` | Database password | `your_password` |
| `DB_NAME` | Database name | `resume_analyzer` |
| `SECRET_KEY` | App secret key | Random string |
| `APP_ENV` | Environment | `development` or `production` |
| `DEBUG` | Debug mode | `True` or `False` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8501` |
| `SERVER_ADDRESS` | Server address | `0.0.0.0` |

---

## Troubleshooting

### Issue: Database Connection Failed

**Solution:**
```bash
# Check environment variables
echo $DB_HOST
echo $DB_PASSWORD

# Test database connection
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME
```

### Issue: Module Not Found

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Docker Build Fails

**Solution:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t resume-screener .
```

### Issue: Streamlit Health Check Fails

**Solution:**
```bash
# Check if Streamlit is running
curl http://localhost:8501/_stcore/health

# Check logs
docker logs <container-id>
```

### Issue: GitHub Actions Failing

**Solution:**
1. Check GitHub Actions logs
2. Verify secrets are set correctly
3. Ensure `requirements.txt` has all dependencies
4. Check Python version compatibility

---

## Production Checklist

Before going live:

- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY` (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Enable HTTPS/SSL
- [ ] Set up database backups
- [ ] Configure monitoring/logging
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Review security settings
- [ ] Test all features in production environment
- [ ] Set up custom domain (optional)

---

## Support

For issues or questions:
- 📧 Create an issue on GitHub
- 📚 Check [Streamlit Docs](https://docs.streamlit.io)
- 🚂 [Railway Docs](https://docs.railway.app)
- 🎨 [Render Docs](https://render.com/docs)

---

**Created by Prachi5555** | [GitHub Repository](https://github.com/Prachi5555/CareerMatch-AI)
