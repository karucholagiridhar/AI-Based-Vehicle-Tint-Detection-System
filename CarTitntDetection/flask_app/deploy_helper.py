#!/usr/bin/env python3
"""
Quick deployment script to verify environment and help with Heroku deployment
"""
import os
import sys
import secrets

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def check_files():
    """Check if required deployment files exist"""
    required_files = [
        'Procfile',
        'runtime.txt',
        'requirements.txt',
        'gunicorn.conf.py',
        'run.py'
    ]
    
    print("📋 Checking deployment files...")
    all_exist = True
    for file in required_files:
        exists = os.path.exists(file)
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_git():
    """Check if git is initialized"""
    print("\n📂 Checking git repository...")
    if os.path.exists('.git'):
        print("  ✓ Git repository initialized")
        return True
    else:
        print("  ✗ Git repository not initialized")
        print("  Run: git init")
        return False

def print_deployment_commands():
    """Print the deployment commands"""
    secret_key = generate_secret_key()
    
    print("\n" + "="*60)
    print("🚀 HEROKU DEPLOYMENT COMMANDS")
    print("="*60)
    
    print("\n1️⃣  Login to Heroku:")
    print("   heroku login")
    
    print("\n2️⃣  Create Heroku app:")
    print("   heroku create your-app-name")
    
    print("\n3️⃣  Add PostgreSQL:")
    print("   heroku addons:create heroku-postgresql:essential-0")
    
    print("\n4️⃣  Set environment variables:")
    print(f"   heroku config:set FLASK_ENV=production")
    print(f"   heroku config:set SECRET_KEY=\"{secret_key}\"")
    print(f"   heroku config:set DEBUG=False")
    print(f"   heroku config:set ROBOFLOW_API_URL=https://serverless.roboflow.com")
    print(f"   heroku config:set ROBOFLOW_API_KEY=\"YOUR_API_KEY_HERE\"")
    print(f"   heroku config:set MODEL_ID=\"YOUR_MODEL_ID_HERE\"")
    print(f"   heroku config:set SESSION_COOKIE_SECURE=True")
    print(f"   heroku config:set MAX_CONTENT_LENGTH=16777216")
    print(f"   heroku config:set UPLOAD_FOLDER=/tmp/uploads")
    
    print("\n5️⃣  Deploy to Heroku:")
    print("   git push heroku main")
    
    print("\n6️⃣  Open your app:")
    print("   heroku open")
    
    print("\n7️⃣  View logs:")
    print("   heroku logs --tail")
    
    print("\n" + "="*60)
    print("💡 TIP: Save the SECRET_KEY above in a secure location!")
    print("="*60)
    print("\n📚 For detailed instructions, see HEROKU_DEPLOYMENT.md")

def main():
    """Main function"""
    print("🔍 Heroku Deployment Checker\n")
    
    files_ok = check_files()
    git_ok = check_git()
    
    if files_ok and git_ok:
        print("\n✅ All checks passed!")
        print_deployment_commands()
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above before deploying.")
        sys.exit(1)

if __name__ == '__main__':
    main()
