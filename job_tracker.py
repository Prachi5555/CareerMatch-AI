import json
from datetime import datetime, date
from database import get_db_connection

def add_job_application(user_id, app_data, resume_id=None):
    """Add a new job application"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT company_id FROM companies WHERE company_name = %s', (app_data['company_name'],))
            company = cursor.fetchone()
            if company:
                company_id = company['company_id']
            else:
                cursor.execute('INSERT INTO companies (company_name) VALUES (%s)', (app_data['company_name'],))
                company_id = cursor.lastrowid
            cursor.execute('INSERT INTO job_applications (user_id, company_id, resume_id, job_title, job_description, job_url, application_date, status, location, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (user_id, company_id, resume_id, app_data['job_title'], app_data.get('job_description'), app_data.get('job_url'), app_data['application_date'], app_data.get('status', 'Applied'), app_data.get('location'), app_data.get('notes')))
            app_id = cursor.lastrowid
            cursor.execute('INSERT INTO application_status (application_id, status, notes) VALUES (%s, %s, %s)', (app_id, app_data.get('status', 'Applied'), 'Initial application'))
            return True, app_id, "Application added successfully!"
    except Exception as e:
        return False, None, f"Failed to add application: {str(e)}"

def get_user_applications(user_id, status=None):
    """Get all job applications for a user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute('SELECT ja.*, c.company_name FROM job_applications ja LEFT JOIN companies c ON ja.company_id = c.company_id WHERE ja.user_id = %s AND ja.status = %s ORDER BY ja.application_date DESC', (user_id, status))
            else:
                cursor.execute('SELECT ja.*, c.company_name FROM job_applications ja LEFT JOIN companies c ON ja.company_id = c.company_id WHERE ja.user_id = %s ORDER BY ja.application_date DESC', (user_id,))
            return cursor.fetchall()
    except Exception as e:
        return []

def update_application_status(application_id, user_id, new_status, notes=None):
    """Update job application status"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE job_applications SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE application_id = %s AND user_id = %s', (new_status, application_id, user_id))
            cursor.execute('INSERT INTO application_status (application_id, status, notes) VALUES (%s, %s, %s)', (application_id, new_status, notes or f'Status changed to {new_status}'))
            return True, "Status updated successfully!"
    except Exception as e:
        return False, f"Failed to update status: {str(e)}"

def get_application_statistics(user_id):
    """Get statistics for user's job applications"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as total_applications, SUM(CASE WHEN status IN (%s, %s) THEN 1 ELSE 0 END) as active_applications, SUM(CASE WHEN status = %s THEN 1 ELSE 0 END) as offers, SUM(CASE WHEN status = %s THEN 1 ELSE 0 END) as rejections FROM job_applications WHERE user_id = %s', ('Applied', 'Interview', 'Offer', 'Rejected', user_id))
            stats = cursor.fetchone()
            if stats and stats['total_applications'] > 0:
                success_rate = (stats['offers'] / stats['total_applications']) * 100 if stats['offers'] else 0
                cursor.execute('SELECT AVG(DATEDIFF(offer_date, application_date)) as avg_days FROM job_applications WHERE user_id = %s AND offer_date IS NOT NULL', (user_id,))
                days_result = cursor.fetchone()
                return {'total_applications': stats['total_applications'], 'active_applications': stats['active_applications'], 'success_rate': success_rate, 'avg_days_to_offer': days_result['avg_days'] or 0 if days_result else 0}
            return {'total_applications': 0, 'active_applications': 0, 'success_rate': 0, 'avg_days_to_offer': 0}
    except Exception as e:
        return None
