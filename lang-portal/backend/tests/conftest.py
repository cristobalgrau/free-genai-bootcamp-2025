import pytest
from flask import Flask
from flask.testing import FlaskClient
import sqlite3
import json
from datetime import datetime, timedelta
import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cmd.server import create_app
from tests.config.test_settings import DATABASE, TESTING, DEBUG
from internal.models.models import db, StudyActivity, Group, StudySession

def seed_database(db_path):
    """Seed the test database with initial data"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create and seed words
    cur.execute("""
        INSERT OR IGNORE INTO words (kanji, romaji, english) 
        VALUES (?, ?, ?)
    """, ("こんにちは", "konnichiwa", "hello"))
    
    # Create and seed groups
    cur.execute("""
        INSERT OR IGNORE INTO groups (name) 
        VALUES (?)
    """, ("Basic Greetings",))
    
    # Create and seed study activities
    cur.execute("""
        INSERT OR IGNORE INTO study_activities (name, description) 
        VALUES (?, ?)
    """, ("Vocabulary Quiz", "Practice your vocabulary"))
    
    # Create word-group associations
    cur.execute("""
        INSERT OR IGNORE INTO words_groups (word_id, group_id)
        SELECT w.id, g.id 
        FROM words w, groups g 
        WHERE w.kanji = 'こんにちは' AND g.name = 'Basic Greetings'
    """)
    
    conn.commit()
    conn.close()

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': TESTING,
        'DEBUG': DEBUG,
        'DATABASE': DATABASE
    })
    return app

@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()

@pytest.fixture
def sample_word():
    return {
        "kanji": "こんにちは",
        "romaji": "konnichiwa",
        "english": "hello",
        "stats": {
            "correct_count": 5,
            "wrong_count": 2
        }
    }

@pytest.fixture
def sample_group():
    return {
        "id": 1,
        "name": "Basic Greetings",
        "word_count": 20
    }

@pytest.fixture
def sample_study_session():
    now = datetime.now()
    return {
        "id": 123,
        "activity_name": "Vocabulary Quiz",
        "group_name": "Basic Greetings",
        "start_time": now.isoformat(),
        "end_time": (now + timedelta(minutes=10)).isoformat(),
        "review_items_count": 20
    }

@pytest.fixture
def setup_study_session(app, client: FlaskClient):
    """Create a study session for testing"""
    with app.app_context():
        # First create a study activity
        study_activity = StudyActivity(
            name="Test Activity",
            description="Test Description"
        )
        db.session.add(study_activity)
        db.session.commit()

        # Get first available group
        group = Group.query.first()
        assert group is not None, "No groups available for testing"

        # Create study session
        study_session = StudySession(
            group_id=group.id,
            study_activity_id=study_activity.id,
            created_at=datetime.now()
        )
        db.session.add(study_session)
        db.session.commit()

        return {
            'id': study_session.id,
            'group_id': study_session.group_id,
            'group_name': group.name,
            'created_at': study_session.created_at.isoformat(),
            'study_activity_id': study_activity.id
        }

@pytest.fixture(autouse=True)
def setup_db(app, client: FlaskClient):
    """Setup initial database state"""
    # Reset database to known state
    client.post('/api/full_reset')
    
    # Seed database with test data
    seed_database(app.config['DATABASE'])