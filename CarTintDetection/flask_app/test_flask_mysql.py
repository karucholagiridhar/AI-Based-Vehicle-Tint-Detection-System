from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import User, TestResult

app = create_app()

with app.app_context():
    print("="*70)
    print("   Flask App MySQL Connection Test")
    print("="*70)
    
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"\n✅ Database Type: {'MySQL' if 'mysql' in db_uri else 'SQLite'}")
    
    # Test queries
    try:
        user_count = User.query.count()
        test_count = TestResult.query.count()
        
        print(f"✅ Users in database: {user_count}")
        print(f"✅ Test results in database: {test_count}")
        
        # Show first user
        first_user = User.query.first()
        if first_user:
            print(f"✅ First user: {first_user.username} ({first_user.email})")
        
        print("\n" + "="*70)
        print("✅ FLASK APP SUCCESSFULLY CONNECTED TO MYSQL!")
        print("="*70)
        print("\nYour Flask app is now using MySQL database!")
        print("You can start the app with: python run.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
