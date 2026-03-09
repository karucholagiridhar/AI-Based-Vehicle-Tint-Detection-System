"""
SQLite to MySQL Migration Script
==================================
This script migrates all data from SQLite to MySQL database.

Before running:
1. Install MySQL Server (if not already installed)
2. Create a new database: CREATE DATABASE car_tint_detection;
3. Update MySQL connection details below
"""

import sqlite3
import pymysql
import os
from datetime import datetime
import getpass

# ==================== CONFIGURATION ====================
# SQLite Database (source)
SQLITE_DB = os.path.join('instance', 'car_tint_detection.db')

# MySQL Database (destination)
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': None,  # Will be prompted
    'database': 'car_tint_detection',
    'charset': 'utf8mb4'
}

# ========================================================

def create_mysql_tables(mysql_conn):
    """Create tables in MySQL database"""
    cursor = mysql_conn.cursor()
    
    print("\n📋 Creating tables in MySQL...")
    
    # Users table
    cursor.execute("""
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
    print("✅ Created 'users' table")
    
    # Test results table
    cursor.execute("""
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
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_test_type (test_type),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    print("✅ Created 'test_results' table")
    
    # Performance logs table
    cursor.execute("""
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
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    print("✅ Created 'performance_logs' table")
    
    mysql_conn.commit()

def migrate_data(sqlite_conn, mysql_conn):
    """Migrate all data from SQLite to MySQL"""
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    # Get all tables
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in sqlite_cursor.fetchall()]
    
    for table in tables:
        print(f"\n📦 Migrating table: {table}")
        
        # Get all data from SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"   ⚠️  No data in {table}")
            continue
            
        # Get column names
        column_names = [description[0] for description in sqlite_cursor.description]
        
        # Prepare INSERT statement
        placeholders = ', '.join(['%s'] * len(column_names))
        columns = ', '.join(column_names)
        
        # For auto-increment tables, we need to skip the ID in INSERT
        if 'id' in column_names:
            # Insert without ID, let MySQL auto-increment
            insert_columns = [col for col in column_names if col != 'id']
            insert_placeholders = ', '.join(['%s'] * len(insert_columns))
            insert_sql = f"INSERT INTO {table} ({', '.join(insert_columns)}) VALUES ({insert_placeholders})"
            
            # Prepare data without ID column
            id_index = column_names.index('id')
            insert_data = []
            for row in rows:
                row_list = list(row)
                row_list.pop(id_index)
                insert_data.append(tuple(row_list))
        else:
            insert_sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            insert_data = rows
        
        # Insert data in batches
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(insert_data), batch_size):
            batch = insert_data[i:i + batch_size]
            mysql_cursor.executemany(insert_sql, batch)
            total_inserted += len(batch)
            print(f"   ✅ Inserted {total_inserted}/{len(rows)} rows")
        
        mysql_conn.commit()
        print(f"   ✅ Completed migrating {table} ({len(rows)} rows)")

def verify_migration(sqlite_conn, mysql_conn):
    """Verify that all data was migrated correctly"""
    print("\n\n🔍 Verifying migration...")
    
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    # Get all tables
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in sqlite_cursor.fetchall()]
    
    all_match = True
    
    for table in tables:
        # Count rows in SQLite
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        sqlite_count = sqlite_cursor.fetchone()[0]
        
        # Count rows in MySQL
        mysql_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        mysql_count = mysql_cursor.fetchone()[0]
        
        if sqlite_count == mysql_count:
            print(f"✅ {table}: {sqlite_count} rows (match)")
        else:
            print(f"❌ {table}: SQLite={sqlite_count}, MySQL={mysql_count} (mismatch!)")
            all_match = False
    
    return all_match

def main():
    print("="*70)
    print("   SQLite to MySQL Migration Tool")
    print("="*70)
    
    # Check if SQLite database exists
    if not os.path.exists(SQLITE_DB):
        print(f"\n❌ Error: SQLite database not found at {SQLITE_DB}")
        return
    
    # Get MySQL password
    print("\n🔐 MySQL Authentication Required")
    MYSQL_CONFIG['password'] = getpass.getpass("Enter MySQL root password: ")
    
    print(f"\n📂 SQLite Database: {SQLITE_DB}")
    print(f"🗄️  MySQL Database: {MYSQL_CONFIG['user']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}")
    
    # Connect to databases
    try:
        print("\n🔌 Connecting to databases...")
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        print("✅ Connected to SQLite")
        
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        print("✅ Connected to MySQL")
        
    except Exception as e:
        print(f"\n❌ Connection Error: {e}")
        print("\nPlease ensure:")
        print("1. MySQL server is running")
        print("2. Database 'car_tint_detection' exists (CREATE DATABASE car_tint_detection;)")
        print("3. MySQL credentials in this script are correct")
        return
    
    try:
        # Create tables in MySQL
        create_mysql_tables(mysql_conn)
        
        # Migrate data
        migrate_data(sqlite_conn, mysql_conn)
        
        # Verify migration
        if verify_migration(sqlite_conn, mysql_conn):
            print("\n" + "="*70)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("="*70)
            print("\nNext steps:")
            print("1. Update your .env file with MySQL connection string")
            print("2. Restart your Flask application")
            print("3. Test the application to ensure everything works")
        else:
            print("\n⚠️  Migration completed with some mismatches. Please review.")
        
    except Exception as e:
        print(f"\n❌ Migration Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        sqlite_conn.close()
        mysql_conn.close()
        print("\n🔌 Database connections closed")

if __name__ == '__main__':
    main()
