# 📊 Database Access Guide

## 🚀 Quick Commands

### View All Tables (Complete Data)
```bash
python view_database.py
```
Shows all tables with detailed information - Users, Test Results, and Performance Logs.

---

## 📋 View Individual Tables

### 1️⃣ View USERS Table
```bash
# List all users
python view_users.py

# View specific user details
python view_users.py admin
python view_users.py xyz
```

**Output:**
- User ID, username, email, full name
- Number of tests performed
- Account creation date
- Detailed statistics when viewing specific user

---

### 2️⃣ View TEST RESULTS Table
```bash
# View all test results
python view_test_results.py

# View test results for specific user
python view_test_results.py demo
python view_test_results.py xyz
```

**Shows:**
- Test ID, user, type (image/video/webcam)
- Windows detected (tinted vs clear)
- Confidence scores
- Processing time
- Test date

---

### 3️⃣ View PERFORMANCE LOGS Table
```bash
python view_performance_logs.py
```

**Displays:**
- Overall statistics per user
- Test breakdown (image/video/webcam)
- Detection statistics (tinted vs clear)
- Performance metrics (avg/min/max time)

---

## 🔍 Database Statistics

### Quick Stats
```bash
python check_database.py
```

**Shows:**
- Total users, test results, performance logs
- Recent users and tests
- Database location and type

---

## 💻 Using Python Shell

### Interactive Database Access
```bash
# Start Flask shell
python run.py shell

# Then run queries:
>>> User.query.all()
>>> TestResult.query.filter_by(user_id=1).count()
>>> PerformanceLog.query.first()
```

### Quick Python Queries
```bash
# Count all users
python -c "from app import create_app, db; from app.models import User; app = create_app(); app.app_context().push(); print('Total users:', User.query.count())"

# Find specific user
python -c "from app import create_app, db; from app.models import User; app = create_app(); app.app_context().push(); user = User.query.filter_by(username='admin').first(); print(f'{user.username}: {user.email}') if user else print('Not found')"
```

---

## 📊 Your Current Database

### Statistics
- **Total Users:** 12
- **Total Test Results:** 120
- **Total Performance Logs:** 11

### Database Location
```
instance/car_tint_detection.db
```

### Tables Schema
1. **users** - User accounts and authentication
2. **test_results** - Detection test results
3. **performance_logs** - System performance metrics

---

## 📝 Example Queries

### Most Active User
```python
from app import create_app, db
from app.models import User, TestResult

app = create_app()
with app.app_context():
    users = User.query.all()
    for u in users:
        count = TestResult.query.filter_by(user_id=u.id).count()
        print(f"{u.username}: {count} tests")
```

### Recent Tests
```python
from app import create_app, db
from app.models import TestResult

app = create_app()
with app.app_context():
    recent = TestResult.query.order_by(TestResult.created_at.desc()).limit(10).all()
    for test in recent:
        print(f"{test.test_type}: {test.windows_detected} windows - {test.created_at}")
```

### Tinted vs Clear Statistics
```python
from app import create_app, db
from app.models import TestResult

app = create_app()
with app.app_context():
    tests = TestResult.query.all()
    total_tinted = sum(t.tinted_windows for t in tests)
    total_clear = sum(t.clear_windows for t in tests)
    print(f"Tinted: {total_tinted}, Clear: {total_clear}")
    print(f"Violation Rate: {total_tinted/(total_tinted+total_clear)*100:.1f}%")
```

---

## 🛠️ Database Management

### Initialize Database
```bash
python run.py
# Database is automatically created on first run
```

### Access via SQLite Browser (Optional)
You can use tools like:
- **DB Browser for SQLite** (https://sqlitebrowser.org/)
- **SQLiteStudio** (https://sqlitestudio.pl/)

Open file: `instance/car_tint_detection.db`

---

## ✅ All Available Scripts

| Script | Purpose |
|--------|---------|
| `view_database.py` | Complete database view (all tables) |
| `view_users.py` | Users table only |
| `view_test_results.py` | Test results table only |
| `view_performance_logs.py` | Performance logs table only |
| `check_database.py` | Quick statistics |
| `test_imports.py` | Verify libraries |

---

**Need help?** Run any script without arguments to see usage instructions!
