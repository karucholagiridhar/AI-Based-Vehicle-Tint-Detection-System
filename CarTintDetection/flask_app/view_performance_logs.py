"""
View only PERFORMANCE LOGS table
"""
from app import create_app, db
from app.models import User, PerformanceLog

app = create_app()

with app.app_context():
    print("\n" + "=" * 90)
    print("  📈 PERFORMANCE LOGS TABLE")
    print("=" * 90)
    
    logs = PerformanceLog.query.order_by(PerformanceLog.updated_at.desc()).all()
    print(f"\nTotal Performance Logs: {len(logs)}\n")
    
    if logs:
        for i, log in enumerate(logs, 1):
            user = log.user.username if log.user else 'Unknown'
            
            print(f"\n┌─ Log #{i} (ID: {log.id}) - User: {user}")
            print(f"│")
            print(f"│ 📊 Overall Statistics:")
            print(f"│   Total Tests:       {log.total_tests}")
            print(f"│   Total Detections:  {log.total_detections}")
            print(f"│   Avg Confidence:    {log.average_confidence:.2%}")
            print(f"│")
            print(f"│ 🎨 Test Breakdown:")
            print(f"│   Image Tests:       {log.image_tests}")
            print(f"│   Video Tests:       {log.video_tests}")
            print(f"│   Webcam Tests:      {log.webcam_tests}")
            print(f"│")
            print(f"│ 🎯 Detection Breakdown:")
            print(f"│   Tinted Windows:    {log.tinted_count}")
            print(f"│   Clear Windows:     {log.clear_count}")
            print(f"│   Violation Rate:    {(log.tinted_count/(log.tinted_count+log.clear_count)*100) if (log.tinted_count+log.clear_count) > 0 else 0:.1f}%")
            print(f"│")
            print(f"│ ⚡ Performance Metrics:")
            print(f"│   Average Time:      {log.avg_processing_time:.2f}s")
            print(f"│   Max Time:          {log.max_processing_time:.2f}s")
            print(f"│   Min Time:          {log.min_processing_time:.2f}s")
            print(f"│")
            print(f"│ 📅 Timestamps:")
            print(f"│   Created:           {log.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"│   Last Updated:      {log.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"└{'─' * 70}")
    else:
        print("No performance logs found.")
    
    print("\n" + "=" * 90)
    print()
