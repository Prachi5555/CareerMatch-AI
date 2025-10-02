# 🗄️ MySQL Setup Guide for Resume Analyzer

## ✅ Complete Steps to Use MySQL

---

## **Step 1: Install MySQL Server**

### Option A: Download MySQL (Windows)
1. Download MySQL from: https://dev.mysql.com/downloads/mysql/
2. Run the installer
3. During installation:
   - Choose "Developer Default" or "Server only"
   - Set a **root password** (remember this!)
   - Keep default port: **3306**
4. Complete installation

### Option B: Use Docker (Easier)
```bash
docker run --name resume-mysql -e MYSQL_ROOT_PASSWORD=MyPassword123 -p 3306:3306 -d mysql:8.0
```

---

## **Step 2: Verify MySQL is Running**

```bash
# Check if MySQL is running
mysql --version

# Login to MySQL
mysql -u root -p
# Enter your password when prompted
```

If successful, you'll see:
```
mysql>
```

Type `exit` to quit.

---

## **Step 3: Install Python MySQL Driver**

```bash
pip install mysql-connector-python
```

---

## **Step 4: Update Configuration**

Edit `config.py` and change the password:

```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_ACTUAL_PASSWORD',  # ⚠️ Change this!
    'database': 'resume_analyzer',
    'port': 3306,
    'charset': 'utf8mb4',
    'use_unicode': True,
    'autocommit': False
}
```

---

## **Step 5: Create Database**

Run the setup script:

```bash
python setup_mysql.py
```

This will create the `resume_analyzer` database in MySQL.

---

## **Step 6: Run Your App**

```bash
streamlit run resume_chatbot.py
```

The app will automatically create all tables on first run!

---

## 🔍 Verify Everything Works

### Check Database Exists
```bash
mysql -u root -p
```

Then in MySQL:
```sql
SHOW DATABASES;
USE resume_analyzer;
SHOW TABLES;
```

You should see 8 tables:
- users
- user_profiles
- user_sessions
- resumes
- resume_versions
- resume_analysis_history
- companies
- job_applications
- application_status

---

## 🐛 Troubleshooting

### Error: "Can't connect to MySQL server"
**Solution:**
1. Make sure MySQL is running:
   ```bash
   # Windows
   net start MySQL80
   
   # Or check services
   services.msc
   ```

2. Check if MySQL is listening on port 3306:
   ```bash
   netstat -an | findstr 3306
   ```

### Error: "Access denied for user 'root'"
**Solution:**
- Double-check your password in `config.py`
- Make sure you're using the correct root password

### Error: "Unknown database 'resume_analyzer'"
**Solution:**
- Run `python setup_mysql.py` to create the database

### Error: "Table doesn't exist"
**Solution:**
- The tables are created automatically when you run the app
- Or manually run: `python -c "from database import init_database; init_database()"`

---

## 📊 Database Management

### View All Data
```bash
mysql -u root -p resume_analyzer
```

```sql
-- See all users
SELECT * FROM users;

-- See all resumes
SELECT * FROM resumes;

-- See all job applications
SELECT * FROM job_applications;
```

### Backup Database
```bash
mysqldump -u root -p resume_analyzer > backup.sql
```

### Restore Database
```bash
mysql -u root -p resume_analyzer < backup.sql
```

### Delete Database (if needed)
```bash
mysql -u root -p
```
```sql
DROP DATABASE resume_analyzer;
```

---

## 🔐 Security Best Practices

### 1. Create a Dedicated User (Recommended)

Instead of using root, create a specific user:

```sql
-- Login as root
mysql -u root -p

-- Create user
CREATE USER 'resume_app'@'localhost' IDENTIFIED BY 'strong_password_here';

-- Grant permissions
GRANT ALL PRIVILEGES ON resume_analyzer.* TO 'resume_app'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;
```

Then update `config.py`:
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'resume_app',  # Changed from 'root'
    'password': 'strong_password_here',
    'database': 'resume_analyzer',
    ...
}
```

### 2. Use Environment Variables

Create `.env` file:
```
MYSQL_PASSWORD=your_password_here
```

Update `config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': 'resume_analyzer',
    ...
}
```

Install python-dotenv:
```bash
pip install python-dotenv
```

---

## 📈 Performance Tips

### 1. Add Indexes (for faster queries)
```sql
USE resume_analyzer;

-- Index on email for faster login
CREATE INDEX idx_users_email ON users(email);

-- Index on user_id for faster lookups
CREATE INDEX idx_resumes_user ON resumes(user_id);
CREATE INDEX idx_applications_user ON job_applications(user_id);
```

### 2. Optimize Queries
The app already uses optimized queries with JOINs and proper indexing.

---

## 🚀 Production Deployment

### For Production Servers:

1. **Use a managed MySQL service:**
   - AWS RDS
   - Google Cloud SQL
   - DigitalOcean Managed Databases
   - Azure Database for MySQL

2. **Update config.py with production credentials:**
```python
MYSQL_CONFIG = {
    'host': 'your-db-server.amazonaws.com',
    'user': 'admin',
    'password': os.getenv('PROD_DB_PASSWORD'),
    'database': 'resume_analyzer',
    'port': 3306,
    ...
}
```

3. **Enable SSL:**
```python
MYSQL_CONFIG = {
    ...
    'ssl_ca': '/path/to/ca-cert.pem',
    'ssl_verify_cert': True
}
```

---

## ✅ Summary

| Step | Command | Status |
|------|---------|--------|
| 1. Install MySQL | Download or Docker | ⬜ |
| 2. Verify MySQL | `mysql --version` | ⬜ |
| 3. Install driver | `pip install mysql-connector-python` | ⬜ |
| 4. Update config | Edit `config.py` | ⬜ |
| 5. Create database | `python setup_mysql.py` | ⬜ |
| 6. Run app | `streamlit run resume_chatbot.py` | ⬜ |

---

## 🎉 You're Done!

Your Resume Analyzer is now running on MySQL!

**Benefits you now have:**
- ✅ Production-ready database
- ✅ Better performance for multiple users
- ✅ Advanced features (transactions, replication)
- ✅ Scalable architecture
- ✅ Industry-standard database

**Next steps:**
- Test the app with resume uploads
- Add job applications
- Monitor database performance
- Set up backups

---

**Need help?** Check the troubleshooting section above or open an issue.
