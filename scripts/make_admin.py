import sqlite3
import sys

def make_admin(username):
    db_path = 'instance/resume_platform.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE user SET is_admin = 1 WHERE username = ?", (username,))
    
    if cursor.rowcount > 0:
        conn.commit()
        print(f"User '{username}' is now an admin")
    else:
        print(f"User '{username}' not found")
    
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/make_admin.py <username>")
        sys.exit(1)
    
    make_admin(sys.argv[1])
