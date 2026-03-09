import sqlite3
import os

# Database path
db_path = os.path.join('instance', 'car_tint_detection.db')

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Function to print table
def print_table(table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"\n{'='*100}")
    print(f"TABLE: {table_name.upper()}")
    print(f"{'='*100}")
    
    # Print header
    header = " | ".join(f"{col:15}" for col in columns)
    print(header)
    print("-" * len(header))
    
    # Print rows
    if rows:
        for row in rows:
            row_str = " | ".join(f"{str(val)[:15]:15}" for val in row)
            print(row_str)
        print(f"\nTotal rows: {len(rows)}")
    else:
        print("No data found")
    print()

# Show all tables
print("\n" + "="*100)
print("DATABASE: car_tint_detection.db")
print("="*100)

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\nTables found: {', '.join([t[0] for t in tables])}\n")

# Display each table
for table in tables:
    table_name = table[0]
    print_table(table_name)

conn.close()
