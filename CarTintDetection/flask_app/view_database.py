"""
Database Viewer - View all tables and their data
"""
from app import create_app, db
from app.models import User, TestResult, PerformanceLog
import json

app = create_app()

def print_separator(char="=", length=80):
    print(char * length)

def print_table_header(title):
    print("\n")
    print_separator("=")
    print(f"  {title}")
    print_separator("=")

with app.app_context():
    print_separator("*")
    print("  DATABASE VIEWER - CAR TINT DETECTION SYSTEM")
    print_separator("*")
    
    # ===========================
    # TABLE 1: USERS
    # ===========================
    print_table_header("TABLE 1: USERS")
    users = User.query.all()
    print(f"\nTotal Users: {len(users)}\n")
    
    if users:
        for i, user in enumerate(users, 1):
            print(f"\n┌─ User #{i} (ID: {user.id})")
            print(f"│ Username:      {user.username}")
            print(f"│ Email:         {user.email}")
            print(f"│ Full Name:     {user.full_name}")
            print(f"│ Phone:         {user.phone}")
            print(f"│ Organization:  {user.organization or 'N/A'}")
            print(f"│ Created:       {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"│ Updated:       {user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Count user's test results
            test_count = TestResult.query.filter_by(user_id=user.id).count()
            print(f"│ Total Tests:   {test_count}")
            print(f"└{'─' * 50}")
    else:
        print("  No users found.")
    
    # ===========================
    # TABLE 2: TEST RESULTS
    # ===========================
    print_table_header("TABLE 2: TEST RESULTS")
    test_results = TestResult.query.order_by(TestResult.created_at.desc()).all()
    print(f"\nTotal Test Results: {len(test_results)}\n")
    
    if test_results:
        # Summary statistics
        image_tests = [t for t in test_results if t.test_type == 'image']
        video_tests = [t for t in test_results if t.test_type == 'video']
        webcam_tests = [t for t in test_results if t.test_type == 'webcam']
        
        print("📊 Summary:")
        print(f"   Image Tests:  {len(image_tests)}")
        print(f"   Video Tests:  {len(video_tests)}")
        print(f"   Webcam Tests: {len(webcam_tests)}")
        
        total_tinted = sum(t.tinted_windows for t in test_results)
        total_clear = sum(t.clear_windows for t in test_results)
        print(f"   Total Tinted: {total_tinted}")
        print(f"   Total Clear:  {total_clear}")
        
        print("\n📋 Detailed Records:")
        for i, test in enumerate(test_results, 1):
            print(f"\n┌─ Test #{i} (ID: {test.id})")
            print(f"│ User:          {test.user.username} (ID: {test.user_id})")
            print(f"│ Type:          {test.test_type.upper()}")
            print(f"│ File:          {test.original_filename}")
            print(f"│ File Path:     {test.file_path or 'N/A'}")
            print(f"│ Output:        {test.output_path or 'N/A'}")
            print(f"│")
            print(f"│ 🎯 Detection Results:")
            print(f"│    Windows Detected: {test.windows_detected}")
            print(f"│    Tinted Windows:   {test.tinted_windows}")
            print(f"│    Clear Windows:    {test.clear_windows}")
            print(f"│")
            print(f"│ 📊 Metrics:")
            print(f"│    Avg Confidence:   {test.average_confidence:.2%}")
            print(f"│    Total Detections: {test.total_detections}")
            print(f"│    Processing Time:  {test.processing_time:.2f}s")
            print(f"│    Model Version:    {test.model_version}")
            print(f"│")
            print(f"│ Status:        {test.status}")
            if test.error_message:
                print(f"│ Error:         {test.error_message}")
            print(f"│ Created:       {test.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show predictions if available
            if test.predictions_json:
                try:
                    predictions = json.loads(test.predictions_json)
                    print(f"│")
                    print(f"│ 🔍 Raw Predictions: ({len(predictions)} predictions)")
                    for j, pred in enumerate(predictions[:3], 1):  # Show first 3
                        cls = pred.get('class', 'unknown')
                        conf = pred.get('confidence', 0)
                        print(f"│    {j}. {cls.upper()}: {conf:.2%} confidence")
                    if len(predictions) > 3:
                        print(f"│    ... and {len(predictions) - 3} more")
                except:
                    print(f"│ Raw Predictions: (parsing error)")
            
            print(f"└{'─' * 50}")
            
            if i >= 10:  # Limit to first 10 to avoid too much output
                remaining = len(test_results) - 10
                if remaining > 0:
                    print(f"\n... and {remaining} more test results (showing first 10)")
                break
    else:
        print("  No test results found.")
    
    # ===========================
    # TABLE 3: PERFORMANCE LOGS
    # ===========================
    print_table_header("TABLE 3: PERFORMANCE LOGS")
    perf_logs = PerformanceLog.query.order_by(PerformanceLog.updated_at.desc()).all()
    print(f"\nTotal Performance Logs: {len(perf_logs)}\n")
    
    if perf_logs:
        for i, log in enumerate(perf_logs, 1):
            print(f"\n┌─ Performance Log #{i} (ID: {log.id})")
            print(f"│ User:          {log.user.username} (ID: {log.user_id})")
            print(f"│")
            print(f"│ 📊 Overall Statistics:")
            print(f"│    Total Tests:      {log.total_tests}")
            print(f"│    Total Detections: {log.total_detections}")
            print(f"│    Avg Confidence:   {log.average_confidence:.2%}")
            print(f"│")
            print(f"│ 🎨 Test Breakdown:")
            print(f"│    Image Tests:      {log.image_tests}")
            print(f"│    Video Tests:      {log.video_tests}")
            print(f"│    Webcam Tests:     {log.webcam_tests}")
            print(f"│")
            print(f"│ 🎯 Detection Breakdown:")
            print(f"│    Tinted Windows:   {log.tinted_count}")
            print(f"│    Clear Windows:    {log.clear_count}")
            print(f"│")
            print(f"│ ⚡ Performance:")
            print(f"│    Avg Time:         {log.avg_processing_time:.2f}s")
            print(f"│    Max Time:         {log.max_processing_time:.2f}s")
            print(f"│    Min Time:         {log.min_processing_time:.2f}s")
            print(f"│")
            print(f"│ Created:       {log.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"│ Updated:       {log.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"└{'─' * 50}")
    else:
        print("  No performance logs found.")
    
    # ===========================
    # SUMMARY
    # ===========================
    print_table_header("DATABASE SUMMARY")
    print(f"""
    Total Records:
    • Users:            {len(users)}
    • Test Results:     {len(test_results)}
    • Performance Logs: {len(perf_logs)}
    
    Database File: instance/car_tint_detection.db
    Database Type: SQLite
    """)
    print_separator("*")
    print("  ✅ Database view complete!")
    print_separator("*")
