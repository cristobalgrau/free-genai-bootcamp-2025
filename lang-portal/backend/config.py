import os
from pathlib import Path

class Config:
    """Application configuration"""
    # Base directory
    BASE_DIR = Path(__file__).resolve().parent

    # Database
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/db/words.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask settings
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'dev'  # Change this in production!

    # API settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True