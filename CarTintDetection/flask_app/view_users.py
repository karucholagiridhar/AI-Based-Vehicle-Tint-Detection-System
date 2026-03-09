"""
View only USERS table
"""
from app import create_app, db
from app.models import User, TestResult
import sys

app = create_app()

with app.app_context():
    print("\n" + "=" * 80)
    print("  👥 USERS TABLE")
    print("=" * 80)
    
    users = User.query.order_by(User.created_at.desc()).all()
    print(f"\nTotal Users: {len(users)}\n")
    
    # Table header
    print(f"{'ID':<5} {'Username':<15} {'Email':<25} {'Full Name':<15} {'Tests':<8} {'Created':<20}")
    print("-" * 95)
    
    for user in users:
        test_count = TestResult.query.filter_by(user_id=user.id).count()
        created = user.created_at.strftime('%Y-%m-%d %H:%M')
        print(f"{user.id:<5} {user.username:<15} {user.email:<25} {user.full_name:<15} {test_count:<8} {created:<20}")
    
    print("\n" + "=" * 80)
    
    # Show details for specific user if provided
    if len(sys.argv) > 1:
        username = sys.argv[1]
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"\n📋 DETAILED INFO FOR: {username}")
            print("-" * 80)
            print(f"ID:           {user.id}")
            print(f"Username:     {user.username}")
            print(f"Email:        {user.email}")
            print(f"Full Name:    {user.full_name}")
            print(f"Phone:        {user.phone}")
            print(f"Organization: {user.organization or 'N/A'}")
            print(f"Created:      {user.created_at}")
            print(f"Updated:      {user.updated_at}")
            print(f"\n🧪 Test Statistics:")
            
            tests = TestResult.query.filter_by(user_id=user.id).all()
            image_tests = len([t for t in tests if t.test_type == 'image'])
            video_tests = len([t for t in tests if t.test_type == 'video'])
            webcam_tests = len([t for t in tests if t.test_type == 'webcam'])
            
            print(f"Total Tests:   {len(tests)}")
            print(f"  - Image:     {image_tests}")
            print(f"  - Video:     {video_tests}")
            print(f"  - Webcam:    {webcam_tests}")
            
            if tests:
                total_tinted = sum(t.tinted_windows for t in tests)
                total_clear = sum(t.clear_windows for t in tests)
                avg_conf = sum(t.average_confidence for t in tests) / len(tests)
                
                print(f"\nDetection Results:")
                print(f"  Tinted Windows: {total_tinted}")
                print(f"  Clear Windows:  {total_clear}")
                print(f"  Avg Confidence: {avg_conf:.2%}")
        else:
            print(f"\n❌ User '{username}' not found")
    else:
        print("\n💡 TIP: Run 'python view_users.py <username>' to see detailed info")
    
    print()
