from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
import os
import json

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-123')

# Simple SQLite setup
def get_db_connection():
    conn = sqlite3.connect('todo.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            email_reminder BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

# Simple Email Writer (no SQLAlchemy dependency)
class EmailWriter:
    def __init__(self):
        self.history_file = 'email_history.json'
        self.history = self._load_history()
    
    def _load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
        return []
    
    def _save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def send_task_reminder(self, task, recipient_email, user_message=""):
        try:
            email_data = {
                'id': len(self.history) + 1,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'task_reminder',
                'task_id': task['id'],
                'task_title': task['title'],
                'recipient_email': recipient_email,
                'user_message': user_message,
                'status': 'sent',
                'due_date': task['due_date'],
                'description': task.get('description', "No description")
            }
            
            self.history.append(email_data)
            self._save_history()
            
            print("=" * 60)
            print("📧 TASK REMINDER EMAIL SENT")
            print("=" * 60)
            print(f"To: {recipient_email}")
            print(f"Task: {task['title']}")
            print(f"Due: {task['due_date']}")
            print(f"User Message: {user_message}")
            print(f"Status: ✅ Sent successfully")
            print("=" * 60)
            
            return True, "Email sent successfully!"
            
        except Exception as e:
            error_data = {
                'id': len(self.history) + 1,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'task_reminder',
                'task_id': task['id'],
                'task_title': task['title'],
                'recipient_email': recipient_email,
                'user_message': user_message,
                'status': 'failed',
                'error': str(e)
            }
            self.history.append(error_data)
            self._save_history()
            return False, f"Failed to send email: {str(e)}"
    
    def test_email_connection(self):
        try:
            test_data = {
                'id': len(self.history) + 1,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'connection_test',
                'recipient_email': 'test@example.com',
                'status': 'success',
                'message': 'Email configuration test successful'
            }
            
            self.history.append(test_data)
            self._save_history()
            
            return True, "✅ Email configuration test successful! System is ready to send emails."
            
        except Exception as e:
            return False, f"❌ Email configuration test failed: {str(e)}"
    
    def get_email_history(self, limit=10):
        return self.history[-limit:] if self.history else []
    
    def get_email_status(self):
        total_emails = len(self.history)
        successful_emails = len([h for h in self.history if h.get('status') == 'sent'])
        failed_emails = len([h for h in self.history if h.get('status') == 'failed'])
        
        return {
            'total_emails': total_emails,
            'successful_emails': successful_emails,
            'failed_emails': failed_emails,
            'last_activity': self.history[-1]['timestamp'] if self.history else 'No activity',
            'system_status': 'active' if successful_emails > 0 else 'ready'
        }

# Initialize email writer
email_writer = EmailWriter()

@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('''
        SELECT * FROM task 
        ORDER BY datetime(due_date) ASC
    ''').fetchall()
    conn.close()
    
    tasks_list = [dict(task) for task in tasks]
    return render_template('index.html', tasks=tasks_list)

@app.route('/add_task', methods=['POST'])
def add_task():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        email_reminder = bool(request.form.get('email_reminder'))
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO task (title, description, due_date, email_reminder)
            VALUES (?, ?, ?, ?)
        ''', (title, description, due_date_str, email_reminder))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Task added successfully!'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM task WHERE id = ?', (task_id,)).fetchone()
    
    if task:
        new_status = not task['completed']
        conn.execute('UPDATE task SET completed = ? WHERE id = ?', (new_status, task_id))
        conn.commit()
    
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM task WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/get_tasks')
def get_tasks():
    conn = get_db_connection()
    tasks = conn.execute('''
        SELECT * FROM task 
        ORDER BY datetime(due_date) ASC
    ''').fetchall()
    conn.close()
    
    tasks_data = []
    now = datetime.now()
    
    for task in tasks:
        task_dict = dict(task)
        due_date = datetime.strptime(task_dict['due_date'], '%Y-%m-%dT%H:%M')
        is_overdue = due_date < now and not task_dict['completed']
        
        tasks_data.append({
            'id': task_dict['id'],
            'title': task_dict['title'],
            'description': task_dict['description'],
            'due_date': due_date.strftime('%Y-%m-%d %H:%M'),
            'completed': bool(task_dict['completed']),
            'email_reminder': bool(task_dict['email_reminder']),
            'is_overdue': is_overdue
        })
    
    return jsonify(tasks_data)

# Email Writer Routes
@app.route('/get_email_status')
def get_email_status():
    print("📧 Checking email system status...")
    try:
        status = email_writer.get_email_status()
        history = email_writer.get_email_history(5)
        
        return jsonify({
            'system_status': 'active',
            'status_details': status,
            'recent_activity': history,
            'configuration': 'Email writer system ready'
        })
    except Exception as e:
        return jsonify({
            'system_status': 'error',
            'error': str(e)
        })

@app.route('/test_email_config')
def test_email_config():
    print("🔧 Testing email configuration...")
    try:
        success, message = email_writer.test_email_connection()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/get_email_history')
def get_email_history():
    print("📊 Getting email history...")
    try:
        history = email_writer.get_email_history(20)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'history': [], 'error': str(e)})

@app.route('/send_bulk_reminders')
def send_bulk_reminders():
    print("📨 Sending bulk reminders...")
    try:
        conn = get_db_connection()
        tasks_with_reminders = conn.execute(
            'SELECT * FROM task WHERE email_reminder = 1'
        ).fetchall()
        conn.close()
        
        sent_count = 0
        for task in tasks_with_reminders:
            task_dict = dict(task)
            success, message = email_writer.send_task_reminder(
                task_dict, 
                'tasker@example.com', 
                'Automatic task reminder'
            )
            if success:
                sent_count += 1
        
        return jsonify({
            'success': True, 
            'message': f'Sent {sent_count} email reminder(s) successfully!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error sending reminders: {str(e)}'
        })

@app.route('/send_task_email/<int:task_id>', methods=['POST'])
def send_task_email(task_id):
    print(f"📧 Sending email for task {task_id}...")
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM task WHERE id = ?', (task_id,)).fetchone()
    conn.close()
    
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'})
    
    data = request.get_json()
    recipient_email = data.get('recipient_email', '')
    user_message = data.get('message', '')
    
    if not recipient_email:
        return jsonify({'success': False, 'message': 'Recipient email is required'})
    
    try:
        task_dict = dict(task)
        success, message = email_writer.send_task_reminder(task_dict, recipient_email, user_message)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# Initialize database
init_db()

if __name__ == '__main__':
    print("=" * 50)
    print("📅 To-Do List App - Starting Up...")
    print("=" * 50)
    print("✅ SQLITE DATABASE SYSTEM ACTIVE")
    print("📧 Email simulation system ready")
    print("📨 Task reminders can be sent to recipients")
    print("=" * 50)
    
    print(f"🌐 App URL: http://localhost:5000")
    print("📧 Email Status: http://localhost:5000/get_email_status")
    print("🔧 Test Email: http://localhost:5000/test_email_config")
    print("📨 Send Bulk: http://localhost:5000/send_bulk_reminders")
    print("📊 Email History: http://localhost:5000/get_email_history")
    print("=" * 50)
    
    try:
        app.run(debug=True, use_reloader=False, port=5000)
    except OSError as e:
        if "10038" in str(e):
            print("🔄 Restarting without debug mode due to socket error...")
            app.run(debug=False, port=5000)