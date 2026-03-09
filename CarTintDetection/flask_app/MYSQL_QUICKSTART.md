# Quick Start: SQLite to MySQL Migration

## What I've Done For You ✅

1. ✅ Installed MySQL Python drivers (pymysql, cryptography)
2. ✅ Created migration script: `migrate_to_mysql.py`
3. ✅ Created test script: `test_mysql_connection.py`
4. ✅ Updated Flask app to support MySQL
5. ✅ Updated requirements.txt
6. ✅ Created comprehensive setup guide: `MYSQL_SETUP.md`

## What You Need To Do Now

### Option A: Quick Setup (if MySQL is already installed)

```powershell
# 1. Create MySQL database
mysql -u root -p
# Then in MySQL prompt:
CREATE DATABASE car_tint_detection;
exit;

# 2. Create .env file
cd C:\projects\CarTitntDetection\CarTintDetection\flask_app
notepad .env
```

Add this to .env (replace YOUR_PASSWORD):
```
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/car_tint_detection
SECRET_KEY=your-secret-key-here
ROBOFLOW_API_KEY=cto2SFwA0t7Z5g5qqOQi
MODEL_ID=tinted-car-windows-mkpc6-ctdz6/2
```

```powershell
# 3. Update migration script password
notepad migrate_to_mysql.py
# Change line 18: password to YOUR_PASSWORD

# 4. Run migration
python migrate_to_mysql.py

# 5. Test connection
python test_mysql_connection.py

# 6. Start app
python run.py
```

### Option B: Full Setup (MySQL not installed)

See [MYSQL_SETUP.md](MYSQL_SETUP.md) for complete installation guide.

## Files Created

| File | Purpose |
|------|---------|
| `migrate_to_mysql.py` | Migrates all SQLite data to MySQL |
| `test_mysql_connection.py` | Tests MySQL connection |
| `MYSQL_SETUP.md` | Complete setup documentation |
| `.env.example` | Environment variables template |

## Quick Commands Reference

```powershell
# Test MySQL connection
python test_mysql_connection.py

# Migrate data
python migrate_to_mysql.py

# View MySQL data
mysql -u root -p -e "USE car_tint_detection; SELECT * FROM users;"

# Start Flask app
python run.py

# Rollback to SQLite (edit .env)
DATABASE_URL=sqlite:///car_tint_detection.db
```

## Need Help?

1. Read [MYSQL_SETUP.md](MYSQL_SETUP.md) - Full setup guide
2. Check MySQL is running: `services.msc` → MySQL
3. Verify database exists: `mysql -u root -p -e "SHOW DATABASES;"`
4. Test connection: `python test_mysql_connection.py`

## Next Step

**Do you have MySQL installed on your computer?**
- **YES** → Follow "Option A: Quick Setup" above
- **NO** → Download MySQL from: https://dev.mysql.com/downloads/mysql/
  Then follow [MYSQL_SETUP.md](MYSQL_SETUP.md)
