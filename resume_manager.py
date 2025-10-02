import json
from datetime import datetime
from database import get_db_connection

def save_resume(user_id, resume_name, file_path, file_size, file_type, raw_text, extracted_data):
    """Save a new resume for user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE resumes SET is_current = 0 WHERE user_id = %s', (user_id,))
            cursor.execute('INSERT INTO resumes (user_id, resume_name, file_path, file_size, file_type, is_current) VALUES (%s, %s, %s, %s, %s, 1)', (user_id, resume_name, file_path, file_size, file_type))
            resume_id = cursor.lastrowid
            cursor.execute('INSERT INTO resume_versions (resume_id, version_number, raw_text, extracted_data, changes_description) VALUES (%s, 1, %s, %s, %s)', (resume_id, raw_text, json.dumps(extracted_data), 'Initial upload'))
            return True, resume_id, "Resume saved successfully!"
    except Exception as e:
        return False, None, f"Failed to save resume: {str(e)}"

def get_user_resumes(user_id):
    """Get all resumes for a user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT r.*, COUNT(DISTINCT rv.version_id) as version_count, COUNT(DISTINCT rah.analysis_id) as analysis_count FROM resumes r LEFT JOIN resume_versions rv ON r.resume_id = rv.resume_id LEFT JOIN resume_analysis_history rah ON r.resume_id = rah.resume_id WHERE r.user_id = %s GROUP BY r.resume_id ORDER BY r.uploaded_at DESC', (user_id,))
            return cursor.fetchall()
    except Exception as e:
        return []

def save_analysis(resume_id, version_id, job_title, job_description, analysis_results):
    """Save resume analysis results"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO resume_analysis_history (resume_id, version_id, job_title, job_description, selection_probability, missing_skills, strengths, weaknesses, suggestions) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (resume_id, version_id, job_title, job_description, analysis_results.get('selection_probability'), json.dumps(analysis_results.get('missing_skills', [])), json.dumps(analysis_results.get('strengths', [])), json.dumps(analysis_results.get('weaknesses', [])), json.dumps(analysis_results.get('suggestions', []))))
            return True, "Analysis saved!"
    except Exception as e:
        return False, f"Failed: {str(e)}"

def get_analysis_history(resume_id):
    """Get analysis history for a resume"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM resume_analysis_history WHERE resume_id = %s ORDER BY analyzed_at DESC', (resume_id,))
            return cursor.fetchall()
    except:
        return []

def get_resume_improvement_trends(user_id):
    """Get improvement trends"""
    return []
