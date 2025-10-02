"""
MySQL Setup Script for Resume Analyzer
Run this script to create the MySQL database
"""

import mysql.connector
from mysql.connector import Error

# MySQL connection WITHOUT database (to create it)
MYSQL_SETUP_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '@ll@boutme1709',  # ⚠️ CHANGE THIS to your MySQL root password!
    'port': 3306
}

DATABASE_NAME = 'resume_analyzer'

def create_database():
    """Create the resume_analyzer database in MySQL"""
    try:
        # Connect to MySQL server
        print("🔗 Connecting to MySQL server...")
        conn = mysql.connector.connect(**MYSQL_SETUP_CONFIG)
        cursor = conn.cursor()
        
        # Create database
        print(f"📦 Creating database '{DATABASE_NAME}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
        print(f"✅ Database '{DATABASE_NAME}' created successfully!")
        
        # Show databases
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print("\n📊 Available databases:")
        for db in databases:
            print(f"  - {db[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*50)
        print("✅ MySQL setup complete!")
        print("="*50)
        print("\n📝 Next steps:")
        print("1. Update config.py with your MySQL password")
        print("2. Run: pip install mysql-connector-python")
        print("3. Run: streamlit run resume_chatbot.py")
        print("\n")
        
        return True
        
    except Error as e:
        print(f"\n❌ MySQL Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure MySQL server is running")
        print("2. Check your MySQL root password in this file")
        print("3. Verify MySQL is installed: mysql --version")
        print("\n💡 To install MySQL:")
        print("   Download from: https://dev.mysql.com/downloads/mysql/")
        print("   Or use Docker: docker run --name mysql-db -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 -d mysql")
        return False

if __name__ == "__main__":
    print("="*50)
    print("🚀 MySQL Database Setup for Resume Analyzer")
    print("="*50)
    print()
    
    create_database()
