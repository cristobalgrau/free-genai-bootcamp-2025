import os
import sqlite3
from pathlib import Path

class MigrationManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.migrations_dir = Path(__file__).parent.parent / 'db' / 'migrations'
        
    def _init_migration_table(self, cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY,
                migration_name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    def _get_applied_migrations(self, cursor):
        cursor.execute('SELECT migration_name FROM migrations')
        return {row[0] for row in cursor.fetchall()}

    def _get_migration_files(self):
        migration_files = []
        for file in sorted(self.migrations_dir.glob('*.sql')):
            if file.name.startswith('0') and file.name.endswith('.sql'):
                migration_files.append(file)
        return migration_files

    def run_migrations(self):
        print(f"Running migrations from {self.migrations_dir}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Initialize migrations table
        self._init_migration_table(cursor)
        
        # Get applied migrations
        applied_migrations = self._get_applied_migrations(cursor)
        
        # Run pending migrations
        for migration_file in self._get_migration_files():
            if migration_file.name not in applied_migrations:
                print(f"Applying migration: {migration_file.name}")
                
                with open(migration_file, 'r') as f:
                    sql = f.read()
                    
                try:
                    cursor.executescript(sql)
                    cursor.execute(
                        'INSERT INTO migrations (migration_name) VALUES (?)',
                        (migration_file.name,)
                    )
                    conn.commit()
                    print(f"Successfully applied: {migration_file.name}")
                except Exception as e:
                    print(f"Error applying migration {migration_file.name}: {str(e)}")
                    conn.rollback()
                    raise
        
        conn.close()
        print("Migrations completed") 