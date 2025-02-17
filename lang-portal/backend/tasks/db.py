import os
import sqlite3
from pathlib import Path

def migrate():
    """Run all pending migrations"""
    db_path = Path(__file__).parent.parent / "words.db"
    migrations_path = Path(__file__).parent.parent / "db" / "migrations"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create migrations table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS migrations (
        id INTEGER PRIMARY KEY,
        filename TEXT NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Get applied migrations
    cursor.execute("SELECT filename FROM migrations")
    applied = {row[0] for row in cursor.fetchall()}
    
    # Run pending migrations
    for file in sorted(migrations_path.glob("*.sql")):
        if file.name not in applied:
            print(f"Applying migration: {file.name}")
            try:
                with open(file) as f:
                    cursor.executescript(f.read())
                cursor.execute("INSERT INTO migrations (filename) VALUES (?)", (file.name,))
                conn.commit()
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e):
                    print(f"Skipping duplicate column in {file.name}")
                    cursor.execute("INSERT INTO migrations (filename) VALUES (?)", (file.name,))
                    conn.commit()
                else:
                    raise e
    
    # Check current table structure
    cursor.execute(".tables")
    cursor.execute(".schema study_activities")
    
    conn.close()
    print("Migrations completed successfully")

if __name__ == "__main__":
    migrate()