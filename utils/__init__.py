"""
Utils package for To-Do List App
Email sending utilities and helper functions
"""

from .simple_email import send_reminder_email, test_email_connection, email_sender
from .email_writer import email_writer

__all__ = [
    'send_reminder_email', 
    'test_email_connection',
    'email_sender',  # Added missing comma
    'email_writer'
]

