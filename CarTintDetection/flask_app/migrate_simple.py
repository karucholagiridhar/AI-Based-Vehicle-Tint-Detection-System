"""
Simple MySQL Migration Script
Run with: python migrate_simple.py YOUR_MYSQL_PASSWORD
"""

import sqlite3
import pymysql
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python migrate_simple.py YOUR_MYSQL_PASSWORD")
    print("\nOr update the PASSWORD variable in this file and run: python migrate_simple.py")
    sys.exit(1)

# MySQL Password from command line
MYSQL_PASSWORD = sys.argv[1]

# Configuration
SQLITE_DB = os.path.join('instance', 'car_tint_detection.db')
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': MYSQL_PASSWORD,
    'database': 'car_tint_detection',
    'charset': 'utf8mb4'
}

print("="*70)
print("   SQLite to MySQL Migration")
print("="*70)

# Connect
print("\n🔌 Connecting...")
sqlite_conn = sqlite3.connect(SQLITE_DB)
mysql_conn = pymysql.connect(**MYSQL_CONFIG)
mysql_cursor = mysql_conn.cursor()

# Create tables
print("\n📋 Creating tables...")

mysql_cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        full_name VARCHAR(120),
        phone VARCHAR(20),
        organization VARCHAR(150),
        password_hash VARCHAR(255) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

mysql_cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        test_type VARCHAR(20) NOT NULL,
        file_path TEXT,
        original_filename VARCHAR(255),
        output_path TEXT,
        windows_detected INT DEFAULT 0,
        tinted_windows INT DEFAULT 0,
        clear_windows INT DEFAULT 0,
        average_confidence FLOAT,
        total_detections INT DEFAULT 0,
        processing_time FLOAT,
        model_version VARCHAR(50),
        status VARCHAR(20) DEFAULT 'pending',
        error_message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        predictions_json JSON,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

mysql_cursor.execute("""
    CREATE TABLE IF NOT EXISTS performance_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        total_tests INT DEFAULT 0,
        total_detections INT DEFAULT 0,
        average_confidence FLOAT,
        image_tests INT DEFAULT 0,
        video_tests INT DEFAULT 0,
        webcam_tests INT DEFAULT 0,
        tinted_count INT DEFAULT 0,
        clear_count INT DEFAULT 0,
        avg_processing_time FLOAT,
        max_processing_time FLOAT,
        min_processing_time FLOAT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

print("✅ Tables created")

# Migrate users
print("\n📦 Migrating users...")
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute("SELECT username, email, full_name, phone, organization, password_hash, created_at, updated_at FROM users")
users = sqlite_cursor.fetchall()
mysql_cursor.executemany(
    "INSERT INTO users (username, email, full_name, phone, organization, password_hash, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
    users
)
print(f"✅ Migrated {len(users)} users")

# Migrate test_results
print("\n📦 Migrating test results...")
sqlite_cursor.execute("SELECT user_id, test_type, file_path, original_filename, output_path, windows_detected, tinted_windows, clear_windows, average_confidence, total_detections, processing_time, model_version, status, error_message, created_at, updated_at, predictions_json FROM test_results")
results = sqlite_cursor.fetchall()
for i in range(0, len(results), 50):
    batch = results[i:i+50]
    mysql_cursor.executemany(
        "INSERT INTO test_results (user_id, test_type, file_path, original_filename, output_path, windows_detected, tinted_windows, clear_windows, average_confidence, total_detections, processing_time, model_version, status, error_message, created_at, updated_at, predictions_json) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        batch
    )
print(f"✅ Migrated {len(results)} test results")

# Migrate performance_logs
print("\n📦 Migrating performance logs...")
sqlite_cursor.execute("SELECT user_id, total_tests, total_detections, average_confidence, image_tests, video_tests, webcam_tests, tinted_count, clear_count, avg_processing_time, max_processing_time, min_processing_time, created_at, updated_at FROM performance_logs")
logs = sqlite_cursor.fetchall()
if logs:
    mysql_cursor.executemany(
        "INSERT INTO performance_logs (user_id, total_tests, total_detections, average_confidence, image_tests, video_tests, webcam_tests, tinted_count, clear_count, avg_processing_time, max_processing_time, min_processing_time, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        logs
    )
    print(f"✅ Migrated {len(logs)} performance logs")
else:
    print("⚠️  No performance logs to migrate")

mysql_conn.commit()

# Verify
print("\n🔍 Verifying...")
mysql_cursor.execute("SELECT COUNT(*) FROM users")
user_count = mysql_cursor.fetchone()[0]
mysql_cursor.execute("SELECT COUNT(*) FROM test_results")
test_count = mysql_cursor.fetchone()[0]
mysql_cursor.execute("SELECT COUNT(*) FROM performance_logs")
log_count = mysql_cursor.fetchone()[0]

print(f"✅ Users: {user_count}")
print(f"✅ Test Results: {test_count}")
print(f"✅ Performance Logs: {log_count}")

sqlite_conn.close()
mysql_conn.close()

print("\n" + "="*70)
print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
print("="*70)
print("\nNext: Update .env file and restart Flask app")
