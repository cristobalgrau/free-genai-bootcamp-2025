import sqlite3
from pathlib import Path

def create_tables():
    """Creates all necessary database tables"""
    db_path = Path(__file__).resolve().parent.parent / "db" / "words.db"
    print(f"Using database at: {db_path}")
    
    # Ensure db directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Execute table creation script
        cursor.executescript("""
            -- Words table
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kanji TEXT NOT NULL,
                romaji TEXT NOT NULL,
                english TEXT NOT NULL,
                parts TEXT
            );

            -- Groups table
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            -- Words-Groups association table
            CREATE TABLE IF NOT EXISTS words_groups (
                word_id INTEGER,
                group_id INTEGER,
                PRIMARY KEY (word_id, group_id),
                FOREIGN KEY (word_id) REFERENCES words (id),
                FOREIGN KEY (group_id) REFERENCES groups (id)
            );

            -- Study Activities table
            CREATE TABLE IF NOT EXISTS study_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                thumbnail_url TEXT,
                description TEXT
            );

            -- Study Sessions table
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                study_activity_id INTEGER,
                FOREIGN KEY (group_id) REFERENCES groups (id),
                FOREIGN KEY (study_activity_id) REFERENCES study_activities (id)
            );

            -- Word Review Items table
            CREATE TABLE IF NOT EXISTS word_review_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER,
                study_session_id INTEGER,
                correct BOOLEAN,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (word_id) REFERENCES words (id),
                FOREIGN KEY (study_session_id) REFERENCES study_sessions (id)
            );
        """)
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Created tables:", [table[0] for table in tables])
        
        conn.commit()
        
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_tables()