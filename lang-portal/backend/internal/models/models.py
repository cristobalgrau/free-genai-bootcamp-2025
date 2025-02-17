from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Word(db.Model):
    __tablename__ = 'words'
    
    id = db.Column(db.Integer, primary_key=True)
    kanji = db.Column(db.String, nullable=False)  # Changed from japanese to kanji
    romaji = db.Column(db.String, nullable=False)
    english = db.Column(db.String, nullable=False)
    parts = db.Column(db.String)  # Store JSON as string
    
    groups = db.relationship('Group', secondary='words_groups', back_populates='words')
    review_items = db.relationship('WordReviewItem', back_populates='word')

    def set_parts(self, parts_dict):
        self.parts = json.dumps(parts_dict)

    def get_parts(self):
        return json.loads(self.parts) if self.parts else {}

class WordGroup(db.Model):
    __tablename__ = 'words_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    
    words = db.relationship('Word', secondary='words_groups', back_populates='groups')
    study_sessions = db.relationship('StudySession', back_populates='group')

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    study_activity_id = db.Column(db.Integer, db.ForeignKey('study_activities.id'))
    
    group = db.relationship('Group', back_populates='study_sessions')
    study_activity = db.relationship('StudyActivity', back_populates='study_sessions')
    review_items = db.relationship('WordReviewItem', back_populates='study_session')

class StudyActivity(db.Model):
    __tablename__ = 'study_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    thumbnail_url = db.Column(db.String)
    description = db.Column(db.String)
    
    study_sessions = db.relationship('StudySession', back_populates='study_activity')

class WordReviewItem(db.Model):
    __tablename__ = 'word_review_items'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    study_session_id = db.Column(db.Integer, db.ForeignKey('study_sessions.id'), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    word = db.relationship('Word', back_populates='review_items')
    study_session = db.relationship('StudySession', back_populates='review_items')