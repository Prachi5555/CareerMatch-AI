"""
MySQL Database Configuration
Uses environment variables for security
For local development: Create a .env file with your credentials
For production: Set environment variables in your cloud platform
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# MySQL Database Configuration
MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'resume_analyzer'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'charset': 'utf8mb4',
    'use_unicode': True,
    'autocommit': False
}

# Application Configuration
APP_CONFIG = {
    'env': os.getenv('APP_ENV', 'development'),
    'debug': os.getenv('DEBUG', 'False').lower() == 'true',
    'secret_key': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
}

# Streamlit Configuration
STREAMLIT_CONFIG = {
    'server_port': int(os.getenv('PORT', '8501')),
    'server_address': os.getenv('SERVER_ADDRESS', '0.0.0.0'),
}
