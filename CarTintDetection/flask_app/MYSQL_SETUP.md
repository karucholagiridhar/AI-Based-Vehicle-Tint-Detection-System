# MySQL Setup Guide for Car Tint Detection

This guide will help you migrate from SQLite to MySQL database.

## Prerequisites

1. **MySQL Server** - Download and install from: https://dev.mysql.com/downloads/mysql/
2. **MySQL Workbench** (Optional, for GUI management): https://dev.mysql.com/downloads/workbench/

## Step-by-Step Setup

### Step 1: Install MySQL Server

**On Windows:**
1. Download MySQL Installer from https://dev.mysql.com/downloads/installer/
2. Run the installer and choose "Developer Default" or "Server only"
3. During installation, set a root password (remember this!)
4. Default port is 3306 (keep this unless you have conflicts)

**Verify Installation:**
```powershell
mysql --version
```

### Step 2: Create Database

Open MySQL command line or MySQL Workbench and run:

```sql
-- Create database
CREATE DATABASE car_tint_detection CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (optional, for security)
CREATE USER 'car_tint_user'@'localhost' IDENTIFIED BY 'your_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON car_tint_detection.* TO 'car_tint_user'@'localhost';
FLUSH PRIVILEGES;

-- Verify database created
SHOW DATABASES;
```

**Using Command Line:**
```powershell
# Login to MySQL
mysql -u root -p

# Then run the SQL commands above
```

### Step 3: Configure Application

Create a `.env` file in the flask_app directory:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development

# MySQL Database Configuration
# Format: mysql+pymysql://username:password@host:port/database_name
DATABASE_URL=mysql+pymysql://root:YOUR_MYSQL_PASSWORD@localhost:3306/car_tint_detection

# If you created a specific user:
# DATABASE_URL=mysql+pymysql://car_tint_user:your_password_here@localhost:3306/car_tint_detection

# Roboflow API (keep existing values)
ROBOFLOW_API_KEY=cto2SFwA0t7Z5g5qqOQi
MODEL_ID=tinted-car-windows-mkpc6-ctdz6/2
ROBOFLOW_API_URL=https://detect.roboflow.com
```

**IMPORTANT:** Replace `YOUR_MYSQL_PASSWORD` with your actual MySQL root password!

### Step 4: Update Migration Script

Edit `migrate_to_mysql.py` and update the MySQL configuration:

```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',          # or 'car_tint_user'
    'password': 'YOUR_PASSWORD_HERE',  # Your MySQL password
    'database': 'car_tint_detection',
    'charset': 'utf8mb4'
}
```

### Step 5: Run Migration

Migrate your existing SQLite data to MySQL:

```powershell
cd C:\projects\CarTitntDetection\CarTintDetection\flask_app
python migrate_to_mysql.py
```

The script will:
- ✅ Create all necessary tables in MySQL
- ✅ Migrate all user data
- ✅ Migrate all test results
- ✅ Migrate all performance logs
- ✅ Verify data integrity

### Step 6: Test Connection

Test if your Flask app can connect to MySQL:

```powershell
python -c "from app import create_app; app = create_app(); print('✅ MySQL connection successful!')"
```

### Step 7: Start Application

```powershell
python run.py
```

Visit http://localhost:5000 and verify:
- ✅ Can login with existing users
- ✅ Can view previous test results
- ✅ Can upload new images/videos
- ✅ Can use webcam detection

## Common MySQL Commands

### View Data in MySQL

```sql
-- Login to MySQL
mysql -u root -p

-- Use database
USE car_tint_detection;

-- Show tables
SHOW TABLES;

-- View users
SELECT * FROM users;

-- View test results
SELECT id, user_id, test_type, tinted_windows, clear_windows, created_at 
FROM test_results 
ORDER BY created_at DESC 
LIMIT 10;

-- Count tests by user
SELECT u.username, COUNT(t.id) as total_tests
FROM users u
LEFT JOIN test_results t ON u.id = t.user_id
GROUP BY u.id, u.username;

-- View database size
SELECT 
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.TABLES
WHERE table_schema = 'car_tint_detection';
```

## Benefits of MySQL over SQLite

✅ **Better Performance**: Handles concurrent users better
✅ **Scalability**: Can handle millions of records efficiently
✅ **Data Integrity**: Better constraint enforcement
✅ **Advanced Features**: Stored procedures, triggers, views
✅ **Production Ready**: Used by major websites worldwide
✅ **Better Backup**: Built-in backup and recovery tools

## Backup Your Data

### Backup MySQL Database

```powershell
# Export database
mysqldump -u root -p car_tint_detection > backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql

# Restore database
mysql -u root -p car_tint_detection < backup_20260309_120000.sql
```

### Keep SQLite Backup

Your original SQLite database is still in:
```
C:\projects\CarTintDetection\CarTintDetection\flask_app\instance\car_tint_detection.db
```

Don't delete it until you've verified everything works in MySQL!

## Troubleshooting

### Error: "Can't connect to MySQL server"
- Ensure MySQL service is running: `services.msc` → Find MySQL → Start
- Check firewall settings
- Verify port 3306 is not blocked

### Error: "Access denied for user"
- Check username and password in `.env` file
- Verify user has correct privileges

### Error: "Unknown database"
- Run: `CREATE DATABASE car_tint_detection;` in MySQL

### Performance Issues
- Add indexes: The migration script already creates key indexes
- Increase MySQL buffer pool size in `my.ini`:
  ```ini
  [mysqld]
  innodb_buffer_pool_size = 256M
  ```

## Rollback to SQLite

If you need to go back to SQLite:

1. Stop the Flask app
2. Edit `.env` file:
   ```env
   DATABASE_URL=sqlite:///car_tint_detection.db
   ```
3. Restart the app

Your SQLite data is still intact!

## Next Steps

After successful migration:
1. Monitor application performance
2. Set up regular MySQL backups
3. Optimize queries if needed
4. Consider setting up MySQL replication for production

## Support

If you encounter issues:
1. Check MySQL error logs: `C:\ProgramData\MySQL\MySQL Server 8.0\Data\*.err`
2. Check Flask application logs
3. Verify all environment variables are set correctly
