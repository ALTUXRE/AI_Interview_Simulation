# database.py

import sqlite3
import datetime

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = sqlite3.connect('interview_data.db')
    cursor = conn.cursor()
    
    # Create a table for interview sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_role TEXT NOT NULL,
            interview_date TEXT NOT NULL
        )
    ''')
    
    # Create a table for interview rounds (question, answer, evaluation)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rounds (
            round_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT,
            evaluation TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_interview_session(job_role):
    """Creates a new interview session record and returns the session ID."""
    conn = sqlite3.connect('interview_data.db')
    cursor = conn.cursor()
    
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO sessions (job_role, interview_date) VALUES (?, ?)", (job_role, current_date))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def save_round(session_id, question, answer, evaluation):
    """Saves a single round of question-answer-evaluation to the database."""
    conn = sqlite3.connect('interview_data.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO rounds (session_id, question, answer, evaluation) VALUES (?, ?, ?, ?)",
        (session_id, question, answer, evaluation)
    )
    
    conn.commit()
    conn.close()

# Add these functions to database.py

def get_all_sessions():
    """Retrieves all past interview sessions, ordered by most recent."""
    conn = sqlite3.connect('interview_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT session_id, job_role, interview_date FROM sessions ORDER BY interview_date DESC")
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_rounds_for_session(session_id):
    """Retrieves all rounds for a specific session ID."""
    conn = sqlite3.connect('interview_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer, evaluation FROM rounds WHERE session_id = ?", (session_id,))
    rounds = cursor.fetchall()
    conn.close()
    return rounds