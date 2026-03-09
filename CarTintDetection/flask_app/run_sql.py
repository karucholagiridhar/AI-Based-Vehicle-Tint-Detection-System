"""
Execute custom SQL queries on the database
"""
import sqlite3
import sys
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'car_tint_detection.db')

if len(sys.argv) < 2:
    print("=" * 80)
    print("  SQL QUERY EXECUTOR")
    print("=" * 80)
    print(f"\nUsage: python run_sql.py \"YOUR SQL QUERY\"")
    print(f"\nDatabase: {db_path}\n")
    print("Examples:")
    print('-' * 80)
    print('python run_sql.py "SELECT * FROM users"')
    print('python run_sql.py "SELECT * FROM users LIMIT 5"')
    print('python run_sql.py "SELECT username, email FROM users"')
    print('python run_sql.py "SELECT COUNT(*) FROM test_results"')
    print('python run_sql.py "SELECT * FROM test_results WHERE user_id = 1"')
    print('python run_sql.py "SELECT * FROM test_results ORDER BY created_at DESC LIMIT 10"')
    print('python run_sql.py "SELECT test_type, COUNT(*) FROM test_results GROUP BY test_type"')
    print('-' * 80)
    sys.exit(0)

query = sys.argv[1]

print(f"\n🔍 Executing query on: {db_path}")
print(f"📝 Query: {query}\n")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(query)
    
    if query.strip().upper().startswith('SELECT'):
        # Get column names
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            print("│ " + " | ".join(f"{col:<20}" for col in columns))
            print("├" + "─" * (len(columns) * 23))
        
        results = cursor.fetchall()
        
        if results:
            for row in results:
                values = [str(v)[:20] if v is not None else "NULL" for v in row]
                print("│ " + " | ".join(f"{v:<20}" for v in values))
            
            print(f"\n✅ {len(results)} row(s) returned")
        else:
            print("(No results)")
    else:
        conn.commit()
        print(f"✅ Query executed successfully")
        print(f"Rows affected: {cursor.rowcount}")
    
    conn.close()

except sqlite3.Error as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
