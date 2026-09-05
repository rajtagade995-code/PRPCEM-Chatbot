-- PRPCEM College Assistant Database Schema
-- Pure SQLite, Rule-Based, No ML

CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    content TEXT,
    category TEXT,
    department TEXT,
    content_hash TEXT,
    last_crawled TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    content TEXT,
    category TEXT,
    department TEXT,
    last_crawled TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    keyword TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT DEFAULT 'General',
    department TEXT,
    academic_year TEXT DEFAULT '2025-26',
    answer TEXT NOT NULL,
    source_url TEXT,
    verified INTEGER DEFAULT 1,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cutoffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_year TEXT NOT NULL,
    course TEXT NOT NULL,
    branch TEXT NOT NULL,
    category TEXT NOT NULL,
    quota TEXT DEFAULT 'Home University',
    cap_round INTEGER NOT NULL,
    cutoff_type TEXT NOT NULL,
    cutoff_value TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_date TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_name TEXT UNIQUE NOT NULL,
    setting_value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast rule-based search
CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url);
CREATE INDEX IF NOT EXISTS idx_pages_category ON pages(category);
CREATE INDEX IF NOT EXISTS idx_docs_url ON documents(url);
CREATE INDEX IF NOT EXISTS idx_cutoffs_lookup ON cutoffs(academic_year, branch, category, cap_round);
CREATE INDEX IF NOT EXISTS idx_knowledge_cat_dept ON knowledge(category, department);
CREATE UNIQUE INDEX IF NOT EXISTS idx_knowledge_question ON knowledge(question);
CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id);
