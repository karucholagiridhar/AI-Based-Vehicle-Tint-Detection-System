"""
Quick database query examples - Access specific table data
"""
from app import create_app, db
from app.models import User, TestResult, PerformanceLog

app = create_app()

# Example queries you can run
print("=" * 60)
print("DATABASE QUERY EXAMPLES")
print("=" * 60)

with app.app_context():
    
    print("\n1️⃣  VIEW ALL USERS:")
    print("   Command: python -c \"from app import create_app, db; from app.models import User; app = create_app(); app.app_context().push(); [print(f'{u.username} - {u.email}') for u in User.query.all()]\"")
    
    print("\n2️⃣  VIEW SPECIFIC USER:")
    print("   Command: python -c \"from app import create_app, db; from app.models import User; app = create_app(); app.app_context().push(); user = User.query.filter_by(username='admin').first(); print(f'{user.full_name} - {user.email}') if user else print('Not found')\"")
    
    print("\n3️⃣  VIEW ALL TEST RESULTS:")
    print("   Command: python view_database.py")
    
    print("\n4️⃣  VIEW TESTS FOR SPECIFIC USER:")
    print("   Command: python query_user_tests.py <username>")
    
    print("\n5️⃣  COUNT RECORDS:")
    print("   Users:        ", User.query.count())
    print("   Test Results: ", TestResult.query.count())
    print("   Perf Logs:    ", PerformanceLog.query.count())
    
    print("\n6️⃣  RECENT ACTIVITY:")
    recent = TestResult.query.order_by(TestResult.created_at.desc()).first()
    if recent:
        print(f"   Last Test: {recent.test_type} by {recent.user.username}")
        print(f"   Date: {recent.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 60)
    print("For full data view, run: python view_database.py")
    print("=" * 60)
