import sqlite3
from contextlib import contextmanager
import config

# Extract the database path from the URL
db_path = config.DATABASE_URL.replace("sqlite:///", "") if config.DATABASE_URL.startswith("sqlite:///") else "nika_memory.db"

def init_db():
    """Initializes the database connection and creates required tables if they don't exist."""
    with get_connection() as conn:
        # Create facts table for durable memory
        conn.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create conversation_log table for full raw history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Commit the transaction
        conn.commit()

@contextmanager
def get_connection():
    """Context manager for checking out a database connection."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()
