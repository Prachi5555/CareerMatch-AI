import streamlit as st
from database import get_db_connection, hash_password, verify_password
from datetime import datetime
import secrets

def register_user(email, password, full_name, phone=None):
    """Register a new user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            password_hash = hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, phone)
                VALUES (%s, %s, %s, %s)
            ''', (email, password_hash, full_name, phone))
            
            user_id = cursor.lastrowid
            
            # Create default profile
            cursor.execute('''
                INSERT INTO user_profiles (user_id)
                VALUES (%s)
            ''', (user_id,))
            
            return True, "Registration successful!"
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return False, "Email already exists!"
        return False, f"Registration failed: {str(e)}"

def login_user(email, password):
    """Login user and create session"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, password_hash, full_name, role
                FROM users
                WHERE email = %s AND is_active = 1
            ''', (email,))
            
            user = cursor.fetchone()
            
            if user and verify_password(password, user['password_hash']):
                # Update last login
                cursor.execute('''
                    UPDATE users
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                ''', (user['user_id'],))
                
                # Create session token
                session_token = secrets.token_hex(32)
                cursor.execute('''
                    INSERT INTO user_sessions (user_id, session_token)
                    VALUES (%s, %s)
                ''', (user['user_id'], session_token))
                
                return True, {
                    'user_id': user['user_id'],
                    'email': email,
                    'full_name': user['full_name'],
                    'role': user['role'],
                    'session_token': session_token
                }
            else:
                return False, "Invalid email or password"
    except Exception as e:
        return False, f"Login failed: {str(e)}"

def logout_user(session_token):
    """Logout user and deactivate session"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_sessions
                SET is_active = 0, logout_time = CURRENT_TIMESTAMP
                WHERE session_token = %s
            ''', (session_token,))
            return True
    except:
        return False

def get_user_profile(user_id):
    """Get user profile information"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.*, p.*
                FROM users u
                LEFT JOIN user_profiles p ON u.user_id = p.user_id
                WHERE u.user_id = %s
            ''', (user_id,))
            return cursor.fetchone()
    except:
        return None

def update_user_profile(user_id, profile_data):
    """Update user profile"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_profiles
                SET current_title = %s,
                    experience_years = %s,
                    education_level = %s,
                    location = %s,
                    linkedin_url = %s,
                    github_url = %s,
                    portfolio_url = %s,
                    bio = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            ''', (
                profile_data.get('current_title'),
                profile_data.get('experience_years'),
                profile_data.get('education_level'),
                profile_data.get('location'),
                profile_data.get('linkedin_url'),
                profile_data.get('github_url'),
                profile_data.get('portfolio_url'),
                profile_data.get('bio'),
                user_id
            ))
            return True, "Profile updated successfully!"
    except Exception as e:
        return False, f"Update failed: {str(e)}"

def check_authentication():
    """Check if user is authenticated"""
    if 'user' not in st.session_state:
        return False
    return True

def require_authentication():
    """Decorator to require authentication"""
    if not check_authentication():
        st.warning("⚠️ Please login to access this feature")
        st.stop()
