import os

# Get the base directory path (backend folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration for test environment
TESTING = True
DEBUG = False
DATABASE = os.path.join(BASE_DIR, 'db', 'words.db')