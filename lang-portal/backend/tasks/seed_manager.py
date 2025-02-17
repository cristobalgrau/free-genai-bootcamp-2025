import json
import sqlite3
from pathlib import Path
from internal.models.models import db, Word, Group, StudyActivity
from datetime import datetime

class SeedManager:
    def __init__(self):
        # Use the same path resolution as create_tables.py
        self.db_path = Path(__file__).resolve().parent.parent / "db" / "words.db"
        self.seeds_dir = Path(__file__).resolve().parent.parent / "db" / "seeds"
        print(f"Initializing SeedManager:")
        print(f"- Database path: {self.db_path}")
        print(f"- Seeds directory: {self.seeds_dir}")

    def seed_data(self, seed_file: str, group_name: str):
        """Seeds data from a JSON file and associates it with a group"""
        try:
            print(f"Seeding data from {seed_file} into group '{group_name}'")
            
            # Read seed file
            seed_path = self.seeds_dir / seed_file
            if not seed_path.exists():
                raise FileNotFoundError(f"Seed file not found: {seed_file}")
                
            with open(seed_path, 'r', encoding='utf-8') as f:
                words_data = json.load(f)
            
            print(f"Found {len(words_data)} words to insert")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Debug: Verify tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print("Available tables:", [table[0] for table in tables])
            
            # Create group if it doesn't exist
            cursor.execute(
                'INSERT OR IGNORE INTO groups (name) VALUES (?)',
                (group_name,)
            )
            
            # Get group id
            cursor.execute('SELECT id FROM groups WHERE name = ?', (group_name,))
            group_id = cursor.fetchone()[0]
            
            # Insert words and create associations
            for word_data in words_data:
                cursor.execute('''
                    INSERT INTO words (kanji, romaji, english, parts)
                    VALUES (?, ?, ?, ?)
                ''', (
                    word_data['kanji'],
                    word_data['romaji'],
                    word_data['english'],
                    json.dumps(word_data.get('parts', {}))
                ))
                
                word_id = cursor.lastrowid
                
                # Create word-group association
                cursor.execute('''
                    INSERT INTO words_groups (word_id, group_id)
                    VALUES (?, ?)
                ''', (word_id, group_id))
            
            conn.commit()
            print(f"Successfully seeded {len(words_data)} words into group '{group_name}'")
            
        except Exception as e:
            print(f"Error seeding data: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    def seed_basic_activity(self):
        """Seeds a basic study activity"""
        print("Seeding basic study activity...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # First check if activity exists
            cursor.execute("SELECT id FROM study_activities WHERE name = ?", ("Vocabulary Quiz",))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute('''
                    INSERT INTO study_activities (name, thumbnail_url, description)
                    VALUES (?, ?, ?)
                ''', (
                    "Vocabulary Quiz",
                    "https://example.com/thumbnail.jpg",
                    "Practice your vocabulary with flashcards"
                ))
                
                conn.commit()
                print("Successfully seeded basic study activity")
            else:
                print("Study activity already exists")
                
        except Exception as e:
            conn.rollback()
            print(f"Error seeding basic activity: {str(e)}")
            raise
        finally:
            conn.close()

    def seed_study_session(self):
        """Seeds a basic study session with some word reviews"""
        print("Seeding study session with reviews...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get first group and activity
            cursor.execute('SELECT id FROM groups LIMIT 1')
            group_id = cursor.fetchone()[0]
            
            cursor.execute('SELECT id FROM study_activities LIMIT 1')
            activity_id = cursor.fetchone()[0]
            
            # Create study session
            cursor.execute('''
                INSERT INTO study_sessions (group_id, created_at, study_activity_id)
                VALUES (?, datetime('now'), ?)
            ''', (group_id, activity_id))
            
            session_id = cursor.lastrowid
            
            # Add word reviews
            cursor.execute('''
                INSERT INTO word_review_items (word_id, study_session_id, correct, created_at)
                SELECT id, ?, true, datetime('now')
                FROM words
                LIMIT 2
            ''', (session_id,))
            
            conn.commit()
            print("Successfully seeded study session with reviews")
            
        except Exception as e:
            conn.rollback()
            print(f"Error seeding study session: {str(e)}")
            raise
        finally:
            conn.close()