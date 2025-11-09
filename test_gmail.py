import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def test_gmail():
    email = os.environ.get('MAIL_USERNAME')
    password = os.environ.get('MAIL_PASSWORD')
    
    print(f"Testing with email: {email}")
    print(f"Password length: {len(password) if password else 0}")
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(email, password)
        print("✅ SUCCESS! Login worked!")
        server.quit()
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == '__main__':
    test_gmail()