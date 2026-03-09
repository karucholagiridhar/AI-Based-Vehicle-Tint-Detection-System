"""
SQLite Database Browser - Interactive Terminal Interface
Opens and explores the SQLite database
"""
import sqlite3
import sys
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'car_tint_detection.db')

print("=" * 80)
print("  🗄️  SQLITE DATABASE BROWSER")
print("=" * 80)
print(f"\n📍 Database File: {db_path}")
print(f"📊 File Size: {os.path.getsize(db_path) / 1024:.2f} KB\n")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=" * 80)
print("  📋 AVAILABLE TABLES")
print("=" * 80)
for i, (table,) in enumerate(tables, 1):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{i}. {table:<30} ({count} records)")

print("\n" + "=" * 80)
print("  📊 TABLE SCHEMAS")
print("=" * 80)

for table, in tables:
    print(f"\n┌─ TABLE: {table}")
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    
    print("│")
    print("│ Columns:")
    for col in columns:
        col_id, name, col_type, not_null, default, pk = col
        pk_marker = " [PRIMARY KEY]" if pk else ""
        null_marker = " NOT NULL" if not_null else ""
        print(f"│   - {name:<20} {col_type:<15}{pk_marker}{null_marker}")
    print("└" + "─" * 78)

# Show sample data from each table
print("\n" + "=" * 80)
print("  📄 SAMPLE DATA (First 3 rows from each table)")
print("=" * 80)

for table, in tables:
    print(f"\n┌─ TABLE: {table}")
    print("│")
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Get sample data
    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
    rows = cursor.fetchall()
    
    if rows:
        # Print column headers
        print("│ " + " | ".join(f"{col[:15]:<15}" for col in columns[:5]))  # Show first 5 cols
        print("│ " + "-" * 75)
        
        # Print rows
        for row in rows:
            values = [str(v)[:15] if v is not None else "NULL" for v in row[:5]]
            print("│ " + " | ".join(f"{v:<15}" for v in values))
    else:
        print("│ (No data)")
    
    print("└" + "─" * 78)

print("\n" + "=" * 80)
print("  💡 QUERY EXAMPLES")
print("=" * 80)
print("""
To run custom SQL queries, use Python:

import sqlite3
conn = sqlite3.connect(r'{}')
cursor = conn.cursor()

# Example queries:
cursor.execute("SELECT * FROM users")
cursor.execute("SELECT * FROM test_results WHERE user_id = 1")
cursor.execute("SELECT COUNT(*) FROM test_results")

results = cursor.fetchall()
for row in results:
    print(row)

conn.close()
""".format(db_path))

print("=" * 80)

# Interactive mode
if len(sys.argv) > 1 and sys.argv[1] == "-i":
    print("\n🔍 INTERACTIVE MODE")
    print("Enter SQL queries (type 'exit' to quit):\n")
    
    while True:
        try:
            query = input("sqlite> ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                break
            
            if not query:
                continue
            
            cursor.execute(query)
            
            if query.lower().startswith('select'):
                results = cursor.fetchall()
                for row in results:
                    print(row)
                print(f"\n({len(results)} rows)")
            else:
                conn.commit()
                print("Query executed successfully")
        
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nGoodbye!")

conn.close()
print("\n✅ Database browser closed")
