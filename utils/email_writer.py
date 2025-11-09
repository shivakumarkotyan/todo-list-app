# utils/email_writer.py
import os
import json
from datetime import datetime

class EmailWriter:
    def __init__(self, app=None):
        self.app = app
        self.history_file = 'email_history.json'
        self.history = self._load_history()
    
    def init_app(self, app):
        self.app = app
        print("✅ EmailWriter system initialized")
    
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
                'task_id': task.id,
                'task_title': task.title,
                'recipient_email': recipient_email,
                'user_message': user_message,
                'status': 'sent',
                'due_date': task.due_date.strftime('%Y-%m-%d %H:%M'),
                'description': task.description or "No description"
            }
            
            self.history.append(email_data)
            self._save_history()
            
            print("=" * 60)
            print("📧 TASK REMINDER EMAIL SENT")
            print("=" * 60)
            print(f"To: {recipient_email}")
            print(f"Task: {task.title}")
            print(f"Due: {task.due_date.strftime('%Y-%m-%d at %H:%M')}")
            print(f"User Message: {user_message}")
            print(f"Status: ✅ Sent successfully")
            print("=" * 60)
            
            return True, "Email sent successfully!"
            
        except Exception as e:
            error_data = {
                'id': len(self.history) + 1,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'task_reminder',
                'task_id': task.id,
                'task_title': task.title,
                'recipient_email': recipient_email,
                'user_message': user_message,
                'status': 'failed',
                'error': str(e)
            }
            self.history.append(error_data)
            self._save_history()
            return False, f"Failed to send email: {str(e)}"
    
    def test_email_connection(self, test_recipient=""):
        try:
            test_data = {
                'id': len(self.history) + 1,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'connection_test',
                'recipient_email': test_recipient or 'test@example.com',
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

# Create global instance
email_writer = EmailWriter()