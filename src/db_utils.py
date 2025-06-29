import sqlite3

DB_PATH = 'data.db'

def get_db_connection(db_path: str = DB_PATH):
    """Return a SQLite connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db(conn: sqlite3.Connection):
    """Create required tables if they don't exist."""
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS ocr_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pdf_file TEXT NOT NULL,
            page INTEGER NOT NULL,
            text TEXT NOT NULL
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS extracted_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chinese TEXT,
            english TEXT,
            ppt_pages TEXT,
            description TEXT
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS aggregated_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chinese TEXT,
            english TEXT,
            ppt_pages TEXT,
            description TEXT
        )"""
    )
    conn.commit()

