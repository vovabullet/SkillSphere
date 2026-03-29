"""
Migration script to add photo_path column to resume table
"""
import sqlite3
import os

db_path = 'instance/resume_platform.db'

if not os.path.exists(db_path):
    print(f"Database file {db_path} not found. Creating new database...")
    os.makedirs('instance', exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.close()
    print("New database created. Run the application to initialize tables.")
    exit(0)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT photo_path FROM resume LIMIT 1")
    print("Column photo_path already exists!")
except sqlite3.OperationalError:
    print("Adding photo_path column...")
    cursor.execute("ALTER TABLE resume ADD COLUMN photo_path TEXT")
    conn.commit()
    print("Migration completed successfully!")

conn.close()
