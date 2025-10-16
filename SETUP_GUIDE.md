# 🚀 Quick Setup Guide - CareerMatch AI

This is a simplified step-by-step guide to get your application running locally and deployed to the cloud.

---

## 📋 Step 1: Local Setup (5 minutes)

### 1.1 Install Prerequisites

- ✅ **Python 3.11+**: [Download here](https://www.python.org/downloads/)
- ✅ **MySQL 8.0+**: [Download here](https://dev.mysql.com/downloads/mysql/)
- ✅ **Git**: [Download here](https://git-scm.com/downloads/)

### 1.2 Clone & Setup

```bash
# Clone repository
git clone https://github.com/Prachi5555/CareerMatch-AI.git
cd CareerMatch-AI

# Create .env file (Windows)
copy .env.example .env

# Edit .env file with your MySQL credentials
# Use Notepad or any text editor
notepad .env
```

**Edit these values in .env:**
```env
DB_USER=prachi
DB_PASSWORD=your_mysql_password_here
```

### 1.3 Install & Run

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Setup database
python setup_mysql.py

# Run application
streamlit run resume_chatbot.py
```

**✅ Done!** Open browser to `http://localhost:8501`

---

## ☁️ Step 2: Deploy to Cloud (10 minutes)

### Option A: Railway (Easiest - Recommended)

1. **Create Account**
   - Go to [railway.app](https://railway.app)
   - Click "Login with GitHub"

2. **Create Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `CareerMatch-AI`

3. **Add Database**
   - Click "New" → "Database" → "MySQL"
   - Railway creates it automatically

4. **Set Environment Variables**
   
   Click on your app → "Variables" tab → Add these:
   
   ```
   APP_ENV=production
   DEBUG=False
   SECRET_KEY=generate-a-random-key-here
   ```
   
   For database, use Railway's reference variables:
   ```
   DB_HOST=${{MySQL.MYSQL_HOST}}
   DB_PORT=${{MySQL.MYSQL_PORT}}
   DB_USER=${{MySQL.MYSQL_USER}}
   DB_PASSWORD=${{MySQL.MYSQL_PASSWORD}}
   DB_NAME=${{MySQL.MYSQL_DATABASE}}
   ```

5. **Deploy**
   - Railway auto-deploys from GitHub
   - Wait 2-3 minutes
   - Click the generated URL to access your app

6. **Initialize Database**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Link to your project
   railway link
   
   # Run setup
   railway run python setup_mysql.py
   ```

**✅ Live!** Your app is now on the internet!

---

### Option B: Render

1. **Create Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Deploy**
   - Click "New" → "Blueprint"
   - Connect your GitHub repo
   - Render reads `render.yaml` and creates everything

3. **Wait**
   - First deployment takes 5-10 minutes
   - Render creates web app + MySQL database

4. **Access**
   - Click the URL in Render dashboard

**✅ Live!** Your app is deployed!

---

## 🔄 Step 3: Enable CI/CD (5 minutes)

### 3.1 GitHub Secrets

Go to your GitHub repo → Settings → Secrets and variables → Actions

Add these secrets:

**For Railway:**
```
RAILWAY_TOKEN=<get from railway CLI: railway whoami>
```

**For Docker Hub (optional):**
```
DOCKERHUB_USERNAME=your_username
DOCKERHUB_TOKEN=your_token
```

### 3.2 How It Works

Now every time you push code to GitHub:

1. ✅ **Tests run automatically** (code quality, security)
2. ✅ **Docker image builds**
3. ✅ **Deploys to Railway** (if on main branch)

**That's it!** You have full CI/CD automation.

---

## 🐳 Step 4: Docker (Optional)

If you want to run with Docker locally:

```bash
# Start everything (app + MySQL)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

Access at `http://localhost:8501`

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Can access the web app URL
- [ ] Can register a new user
- [ ] Can login successfully
- [ ] Can upload a resume
- [ ] Database is working (no connection errors)
- [ ] GitHub Actions are running (check Actions tab)

---

## 🆘 Common Issues

### "Can't connect to database"
**Solution:** Check your `.env` file has correct credentials

### "Module not found"
**Solution:** 
```bash
pip install -r requirements.txt --force-reinstall
```

### "Port already in use"
**Solution:**
```bash
# Kill process on port 8501
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8501 | xargs kill -9
```

### GitHub Actions failing
**Solution:** 
1. Check you added secrets correctly
2. Verify `requirements.txt` has all dependencies
3. Check Actions logs for specific error

---

## 📚 Next Steps

1. **Customize:** Modify the UI in `resume_chatbot.py`
2. **Add Features:** Check `DEPLOYMENT.md` for advanced options
3. **Monitor:** Set up logging and error tracking
4. **Scale:** Add more resources in Railway/Render dashboard

---

## 🎯 Quick Commands Reference

```bash
# Local Development
streamlit run resume_chatbot.py          # Run app
python setup_mysql.py                    # Setup database
pip install -r requirements.txt          # Install deps

# Docker
docker-compose up -d                     # Start
docker-compose logs -f                   # View logs
docker-compose down                      # Stop

# Railway
railway login                            # Login
railway up                               # Deploy
railway logs                             # View logs

# Git
git add .                                # Stage changes
git commit -m "message"                  # Commit
git push origin main                     # Push (triggers CI/CD)
```

---

**Need help?** Create an issue on GitHub or check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides.

**Happy Coding! 🚀**
