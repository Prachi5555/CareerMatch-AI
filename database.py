import hashlib
import os
from datetime import datetime
from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error

# Import MySQL configuration
from config import MYSQL_CONFIG

@contextmanager
def get_db_connection():
    """Context manager for MySQL database connections"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
        
        class MySQLConnection:
            """Wrapper to make MySQL connection compatible with existing code"""
            def __init__(self, connection, cursor):
                self._conn = connection
                self._cursor = cursor
            
            def cursor(self):
                return self._cursor
            
            def commit(self):
                return self._conn.commit()
            
            def rollback(self):
                return self._conn.rollback()
            
            def close(self):
                self._cursor.close()
                return self._conn.close()
            
            def execute(self, *args, **kwargs):
                return self._cursor.execute(*args, **kwargs)
            
            def fetchone(self):
                return self._cursor.fetchone()
            
            def fetchall(self):
                return self._cursor.fetchall()
        
        wrapped_conn = MySQLConnection(conn, cursor)
        
        try:
            yield wrapped_conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    except Error as e:
        print(f"❌ MySQL Connection Error: {e}")
        print("Make sure MySQL server is running and config.py has correct credentials!")
        raise e

def init_database():
    """Initialize MySQL database with all required tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INT PRIMARY KEY AUTO_INCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                phone VARCHAR(50),
                role VARCHAR(50) DEFAULT 'job_seeker',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                profile_id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                current_title VARCHAR(255),
                experience_years INT,
                education_level VARCHAR(100),
                location VARCHAR(255),
                linkedin_url VARCHAR(500),
                github_url VARCHAR(500),
                portfolio_url VARCHAR(500),
                bio TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                ip_address VARCHAR(50),
                user_agent VARCHAR(500),
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                logout_time TIMESTAMP NULL,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Resumes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                resume_id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                resume_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500),
                file_size INT,
                file_type VARCHAR(50),
                is_current BOOLEAN DEFAULT TRUE,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Resume versions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resume_versions (
                version_id INT PRIMARY KEY AUTO_INCREMENT,
                resume_id INT NOT NULL,
                version_number INT NOT NULL,
                raw_text LONGTEXT,
                extracted_data TEXT,
                changes_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resumes(resume_id) ON DELETE CASCADE
            )
        ''')
        
        # Resume analysis history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resume_analysis_history (
                analysis_id INT PRIMARY KEY AUTO_INCREMENT,
                resume_id INT NOT NULL,
                version_id INT,
                job_title VARCHAR(255),
                job_description TEXT,
                selection_probability FLOAT,
                missing_skills TEXT,
                strengths TEXT,
                weaknesses TEXT,
                suggestions TEXT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resumes(resume_id) ON DELETE CASCADE,
                FOREIGN KEY (version_id) REFERENCES resume_versions(version_id) ON DELETE SET NULL
            )
        ''')
        
        # Companies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                company_id INT PRIMARY KEY AUTO_INCREMENT,
                company_name VARCHAR(255) UNIQUE NOT NULL,
                industry VARCHAR(100),
                company_size VARCHAR(50),
                location VARCHAR(255),
                website VARCHAR(500),
                description TEXT,
                rating FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Job applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_applications (
                application_id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                company_id INT,
                resume_id INT,
                job_title VARCHAR(255) NOT NULL,
                job_description TEXT,
                job_url VARCHAR(500),
                application_date DATE NOT NULL,
                status VARCHAR(50) DEFAULT 'Applied',
                salary_min DECIMAL(10,2),
                salary_max DECIMAL(10,2),
                location VARCHAR(255),
                job_type VARCHAR(50),
                notes TEXT,
                follow_up_date DATE,
                interview_date DATETIME,
                offer_date DATE,
                rejection_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE SET NULL,
                FOREIGN KEY (resume_id) REFERENCES resumes(resume_id) ON DELETE SET NULL
            )
        ''')
        
        # Application status history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_status (
                status_id INT PRIMARY KEY AUTO_INCREMENT,
                application_id INT NOT NULL,
                status VARCHAR(50) NOT NULL,
                notes TEXT,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES job_applications(application_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        print("✅ Database initialized successfully!")

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

# Initialize MySQL database on import
try:
    init_database()
except Exception as e:
    print(f"⚠️ Database initialization skipped: {e}")
    print("Database will be created when first accessed.")
