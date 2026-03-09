"""
Check database contents and statistics
"""
from app import create_app, db
from app.models import User, TestResult, PerformanceLog

app = create_app()

with app.app_context():
    print("=" * 60)
    print("DATABASE INFORMATION")
    print("=" * 60)
    
    print(f"\n📍 Database Location: instance/car_tint_detection.db")
    print(f"📊 Database Type: SQLite")
    print(f"🔧 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    
    user_count = User.query.count()
    test_count = TestResult.query.count()
    log_count = PerformanceLog.query.count()
    
    print(f"\n👥 Total Users: {user_count}")
    print(f"🧪 Total Test Results: {test_count}")
    print(f"📈 Total Performance Logs: {log_count}")
    
    if user_count > 0:
        print("\n" + "=" * 60)
        print("RECENT USERS")
        print("=" * 60)
        users = User.query.order_by(User.created_at.desc()).limit(5).all()
        for i, user in enumerate(users, 1):
            print(f"\n{i}. Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Full Name: {user.full_name}")
            print(f"   Organization: {user.organization or 'N/A'}")
            print(f"   Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if test_count > 0:
        print("\n" + "=" * 60)
        print("RECENT TEST RESULTS")
        print("=" * 60)
        tests = TestResult.query.order_by(TestResult.created_at.desc()).limit(5).all()
        for i, test in enumerate(tests, 1):
            print(f"\n{i}. Type: {test.test_type.upper()}")
            print(f"   File: {test.original_filename}")
            print(f"   Windows Detected: {test.windows_detected}")
            print(f"   Tinted: {test.tinted_windows} | Clear: {test.clear_windows}")
            print(f"   Confidence: {test.average_confidence:.2%}")
            print(f"   Processing Time: {test.processing_time:.2f}s")
            print(f"   Status: {test.status}")
            print(f"   Date: {test.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 60)
    print("DATABASE SCHEMA (TABLES)")
    print("=" * 60)
    print("\n📋 Tables:", list(db.metadata.tables.keys()))
    
    print("\n✅ Database check complete!")
