import os

def check_env_file():
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("❌ .env file not found! Creating one...")
        with open(env_file, 'w') as f:
            f.write("""MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
RECIPIENT_EMAIL=your-email@gmail.com
SECRET_KEY=your-secret-key-here
""")
        print("✅ Created .env file with template")
    else:
        print("✅ .env file exists")
        
        # Check content
        with open(env_file, 'r') as f:
            content = f.read()
            lines = content.strip().split('\n')
            
            print(f"📄 .env file has {len(lines)} lines")
            for i, line in enumerate(lines, 1):
                if line.strip() and not line.strip().startswith('#'):
                    print(f"   Line {i}: {line.strip()}")
    
    # Test loading
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ python-dotenv can load the .env file")
        
        # Test a variable
        test_var = os.environ.get('MAIL_SERVER')
        print(f"✅ MAIL_SERVER = {test_var}")
        
    except Exception as e:
        print(f"❌ Error loading .env: {e}")

if __name__ == '__main__':
    check_env_file()