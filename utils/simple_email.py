import os

class EmailSender:
    def __init__(self, app=None):
        self.app = app
        self.demo_mode = True
    
    def init_app(self, app):
        self.app = app
        print("✅ EmailSender initialized in DEMO MODE")

# Create global instance
email_sender = EmailSender()

# Demo functions that don't rely on imports
def send_reminder_email(task, recipient_email):
    """Demo email function - simulates sending email"""
    print(f"📧 DEMO: Would send reminder for task '{task.title}' to {recipient_email}")
    return True

def test_email_connection():
    """Demo email connection test"""
    print("🔧 DEMO: Testing email connection")
    return True, "✅ DEMO MODE: Email functionality is working! (Simulated)"

