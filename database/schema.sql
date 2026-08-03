CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exams (
    id TEXT PRIMARY KEY, -- UUID
    student_id INTEGER NOT NULL,
    student_name TEXT NOT NULL,
    subject TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    provider TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER DEFAULT 30,
    time_taken INTEGER DEFAULT 0, -- in seconds
    score INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 30,
    correct_count INTEGER DEFAULT 0,
    wrong_count INTEGER DEFAULT 0,
    skipped_count INTEGER DEFAULT 0,
    percentage REAL DEFAULT 0.0,
    grade TEXT DEFAULT 'Fail',
    status TEXT DEFAULT 'Pending', -- Pending, Completed, Expired
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id TEXT NOT NULL,
    question_order INTEGER NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL, -- 'A', 'B', 'C', or 'D'
    explanation TEXT NOT NULL,
    FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id TEXT NOT NULL,
    question_id INTEGER NOT NULL,
    student_answer TEXT, -- 'A', 'B', 'C', 'D', or NULL if skipped
    is_correct INTEGER DEFAULT 0, -- 1 for true, 0 for false
    is_marked INTEGER DEFAULT 0, -- 1 for review flag
    FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    certificate_id TEXT UNIQUE NOT NULL, -- Unique Cert ID e.g. CERT-2026-XXXX
    student_id INTEGER NOT NULL,
    exam_id TEXT UNIQUE NOT NULL,
    pdf_location TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE
);
