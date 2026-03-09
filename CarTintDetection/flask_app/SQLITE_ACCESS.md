# 🗄️ SQLite Database Access Guide

## 📍 Your Database Location

**File Path:**
```
C:\projects\CarTitntDetection\CarTitntDetection\flask_app\instance\car_tint_detection.db
```

**File Size:** ~96 KB  
**Type:** SQLite 3 Database  
**Tables:** users, test_results, performance_logs

---

## 🚀 Method 1: Using Python Scripts (EASIEST)

### Browse Database (See Everything)
```bash
cd C:\projects\CarTitntDetection\CarTitntDetection\flask_app
python browse_database.py
```

**Shows:**
- All tables and their record counts
- Table schemas (columns and data types)
- Sample data from each table
- Query examples

### Interactive SQL Mode
```bash
python browse_database.py -i
```

Then type SQL queries:
```sql
sqlite> SELECT * FROM users;
sqlite> SELECT COUNT(*) FROM test_results;
sqlite> exit
```

### Run Custom SQL Queries
```bash
# See all users
python run_sql.py "SELECT * FROM users"

# See specific columns
python run_sql.py "SELECT username, email FROM users"

# Count test results
python run_sql.py "SELECT COUNT(*) FROM test_results"

# Get recent tests
python run_sql.py "SELECT * FROM test_results ORDER BY created_at DESC LIMIT 10"

# Filter by user
python run_sql.py "SELECT * FROM test_results WHERE user_id = 1"

# Group by test type
python run_sql.py "SELECT test_type, COUNT(*) FROM test_results GROUP BY test_type"
```

---

## 🔧 Method 2: Using Python's sqlite3 Module

### Open Python Shell
```bash
cd C:\projects\CarTitntDetection\CarTitntDetection\flask_app
python
```

### Execute SQL Commands
```python
import sqlite3

# Connect to database
conn = sqlite3.connect(r'instance\car_tint_detection.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

# View users table
cursor.execute("SELECT * FROM users")
for row in cursor.fetchall():
    print(row)

# View test results
cursor.execute("SELECT * FROM test_results LIMIT 5")
for row in cursor.fetchall():
    print(row)

# Count records
cursor.execute("SELECT COUNT(*) FROM users")
print(f"Total users: {cursor.fetchone()[0]}")

# Close connection
conn.close()
```

---

## 💻 Method 3: Using sqlite3 Command Line (If Installed)

### Check if sqlite3 is installed
```bash
sqlite3 --version
```

### If NOT installed, download from:
https://www.sqlite.org/download.html

### Open Database
```bash
cd C:\projects\CarTitntDetection\CarTitntDetection\flask_app\instance
sqlite3 car_tint_detection.db
```

### SQLite Commands
```sql
-- List all tables
.tables

-- Show table schema
.schema users
.schema test_results
.schema performance_logs

-- View data
SELECT * FROM users;
SELECT * FROM test_results LIMIT 10;
SELECT * FROM performance_logs;

-- Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM test_results;

-- Formatted output
.mode column
.headers on
SELECT * FROM users;

-- Export to CSV
.mode csv
.output users.csv
SELECT * FROM users;
.output stdout

-- Exit
.quit
```

---

## 📊 Method 4: Using DB Browser for SQLite (GUI Tool)

### Download and Install:
**DB Browser for SQLite** (FREE):
https://sqlitebrowser.org/dl/

### Steps:
1. Download and install DB Browser for SQLite
2. Open the application
3. Click "Open Database"
4. Navigate to: `C:\projects\CarTitntDetection\CarTitntDetection\flask_app\instance`
5. Open: `car_tint_detection.db`

### Features:
- ✅ Visual table browser
- ✅ Execute SQL queries
- ✅ Edit data directly
- ✅ Export to CSV/JSON
- ✅ Database structure viewer

---

## 🎯 Quick Commands (Copy & Paste)

### View Database Structure
```bash
cd C:\projects\CarTitntDetection\CarTitntDetection\flask_app
python browse_database.py
```

### See All Users
```bash
python run_sql.py "SELECT username, email, full_name FROM users"
```

### See All Test Results
```bash
python run_sql.py "SELECT id, test_type, windows_detected, tinted_windows, clear_windows FROM test_results ORDER BY created_at DESC LIMIT 20"
```

### Count Everything
```bash
python run_sql.py "SELECT 'Users' AS table_name, COUNT(*) AS count FROM users UNION SELECT 'Test Results', COUNT(*) FROM test_results UNION SELECT 'Performance Logs', COUNT(*) FROM performance_logs"
```

### User Statistics
```bash
python run_sql.py "SELECT u.username, COUNT(t.id) as total_tests FROM users u LEFT JOIN test_results t ON u.id = t.user_id GROUP BY u.id, u.username ORDER BY total_tests DESC"
```

---

## 📋 Common SQL Queries

### Get User by Username
```sql
SELECT * FROM users WHERE username = 'demo';
```

### Get Tests for Specific User
```sql
SELECT * FROM test_results WHERE user_id = 1;
```

### Get Only Tinted Window Detections
```sql
SELECT * FROM test_results WHERE tinted_windows > 0;
```

### Average Processing Time
```sql
SELECT AVG(processing_time) FROM test_results;
```

### Tests by Type
```sql
SELECT test_type, COUNT(*) as count 
FROM test_results 
GROUP BY test_type;
```

### Recent Failed Tests
```sql
SELECT * FROM test_results 
WHERE status = 'failed' 
ORDER BY created_at DESC;
```

---

## ✅ All Available Tools

| Tool | Command |
|------|---------|
| **Database Browser** | `python browse_database.py` |
| **Interactive SQL** | `python browse_database.py -i` |
| **Run SQL Query** | `python run_sql.py "QUERY"` |
| **View All Tables** | `python view_database.py` |
| **View Users** | `python view_users.py` |
| **View Test Results** | `python view_test_results.py` |
| **View Performance** | `python view_performance_logs.py` |

---

**Your database is located at:**
```
C:\projects\CarTitntDetection\CarTitntDetection\flask_app\instance\car_tint_detection.db
```

Start with: `python browse_database.py` to see everything!
