import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('inventory.db')

# Export each table to CSV
tables = ['vendor_sales_summary', 'purchases', 'sales']

for table in tables:
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        df.to_csv(f'{table}.csv', index=False)
        print(f"✅ Exported {table}.csv ({len(df)} rows)")
    except Exception as e:
        print(f"❌ Error exporting {table}: {e}")

conn.close()
print("\n✅ All exports complete!")
