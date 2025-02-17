-- Create words table
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kanji TEXT NOT NULL,
    romaji TEXT NOT NULL,
    english TEXT NOT NULL,
    parts TEXT
);

-- Create groups table
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Create words-groups association table
CREATE TABLE IF NOT EXISTS words_groups (
    word_id INTEGER,
    group_id INTEGER,
    PRIMARY KEY (word_id, group_id),
    FOREIGN KEY (word_id) REFERENCES words (id),
    FOREIGN KEY (group_id) REFERENCES groups (id)
);

-- Create study activities table
CREATE TABLE IF NOT EXISTS study_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL DEFAULT 'Vocabulary Quiz',
    thumbnail_url TEXT DEFAULT 'https://example.com/thumbnail.jpg',
    description TEXT DEFAULT 'Practice your vocabulary with flashcards'
);

-- Create study sessions table
CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    study_activity_id INTEGER,
    FOREIGN KEY (group_id) REFERENCES groups (id),
    FOREIGN KEY (study_activity_id) REFERENCES study_activities (id)
);

-- Create word review items table
CREATE TABLE IF NOT EXISTS word_review_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER,
    study_session_id INTEGER,
    correct BOOLEAN,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words (id),
    FOREIGN KEY (study_session_id) REFERENCES study_sessions (id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_words_groups_group_id ON words_groups(group_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_group_id ON study_sessions(group_id);
CREATE INDEX IF NOT EXISTS idx_word_review_items_word_id ON word_review_items(word_id);
CREATE INDEX IF NOT EXISTS idx_word_review_items_session_id ON word_review_items(study_session_id);