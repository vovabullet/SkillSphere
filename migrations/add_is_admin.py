import sqlite3
import os

def migrate():
    db_path = 'instance/resume_platform.db'
    if not os.path.exists(db_path):
        print("Database not found, skipping migration")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(user)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'is_admin' not in columns:
        print("Adding is_admin column to user table...")
        cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        conn.commit()
        print("Migration complete: is_admin column added")
    else:
        print("is_admin column already exists")
    
    conn.close()

if __name__ == '__main__':
    migrate()
