"""
Test MySQL Database Connection
================================
This script tests the connection to your MySQL database
"""

import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mysql_connection():
    """Test MySQL connection using DATABASE_URL from .env"""
    
    print("="*70)
    print("   MySQL Connection Test")
    print("="*70)
    
    # Get DATABASE_URL
    database_url = os.environ.get('DATABASE_URL', '')
    
    if not database_url:
        print("\n❌ DATABASE_URL not found in environment variables")
        print("\nPlease create a .env file with:")
        print("DATABASE_URL=mysql+pymysql://username:password@host:port/database")
        return False
    
    if not database_url.startswith('mysql'):
        print(f"\n⚠️  DATABASE_URL is set to: {database_url}")
        print("This appears to be SQLite, not MySQL")
        return False
    
    print(f"\n🔍 Database URL: {database_url.replace(database_url.split(':')[2].split('@')[0], '***')}")
    
    # Parse DATABASE_URL
    # Format: mysql+pymysql://user:password@host:port/database
    try:
        # Remove mysql+pymysql://
        url_parts = database_url.replace('mysql+pymysql://', '')
        
        # Split user:password@host:port/database
        auth_and_host = url_parts.split('/')
        database = auth_and_host[1] if len(auth_and_host) > 1 else 'car_tint_detection'
        
        user_pass_host = auth_and_host[0]
        
        # Split user:password from host:port
        auth, host_port = user_pass_host.split('@')
        user, password = auth.split(':')
        
        # Split host and port
        if ':' in host_port:
            host, port = host_port.split(':')
            port = int(port)
        else:
            host = host_port
            port = 3306
        
        print(f"🔧 Host: {host}")
        print(f"🔧 Port: {port}")
        print(f"🔧 User: {user}")
        print(f"🔧 Database: {database}")
        
    except Exception as e:
        print(f"\n❌ Error parsing DATABASE_URL: {e}")
        print("\nExpected format:")
        print("DATABASE_URL=mysql+pymysql://username:password@localhost:3306/car_tint_detection")
        return False
    
    # Test connection
    try:
        print("\n🔌 Attempting to connect to MySQL...")
        
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        print("✅ Successfully connected to MySQL!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ MySQL Version: {version[0]}")
        
        # Show tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print(f"\n📋 Tables in database ({len(tables)}):")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   - {table[0]}: {count} rows")
        else:
            print("\n⚠️  No tables found. Run migration script first!")
        
        conn.close()
        print("\n" + "="*70)
        print("✅ MySQL CONNECTION TEST PASSED!")
        print("="*70)
        return True
        
    except pymysql.Error as e:
        print(f"\n❌ MySQL Connection Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure MySQL server is running")
        print("2. Verify username and password are correct")
        print("3. Check if database exists: CREATE DATABASE car_tint_detection;")
        print("4. Verify user has access to the database")
        return False
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

def test_flask_app_connection():
    """Test Flask app's database connection"""
    print("\n\n" + "="*70)
    print("   Flask App Database Test")
    print("="*70)
    
    try:
        from app import create_app, db
        
        app = create_app()
        
        with app.app_context():
            print(f"\n🔧 SQLAlchemy Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
            # Test database connection
            db.engine.connect()
            print("✅ Flask app successfully connected to database!")
            
            # Try to query tables
            from app.models import User, TestResult
            
            user_count = User.query.count()
            test_count = TestResult.query.count()
            
            print(f"✅ Users in database: {user_count}")
            print(f"✅ Test results in database: {test_count}")
            
            print("\n" + "="*70)
            print("✅ FLASK APP CONNECTION TEST PASSED!")
            print("="*70)
            return True
            
    except Exception as e:
        print(f"\n❌ Flask App Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Test direct MySQL connection
    mysql_ok = test_mysql_connection()
    
    # Test Flask app connection
    if mysql_ok:
        flask_ok = test_flask_app_connection()
        
        if flask_ok:
            print("\n\n🎉 All tests passed! Your MySQL database is ready to use.")
        else:
            print("\n\n⚠️  MySQL works but Flask app connection failed.")
            print("Check your Flask configuration and models.")
    else:
        print("\n\n❌ MySQL connection failed. Please fix the issues above.")
        print("\nHave you:")
        print("1. Installed MySQL Server?")
        print("2. Created the database 'car_tint_detection'?")
        print("3. Created a .env file with correct DATABASE_URL?")
