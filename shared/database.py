import sqlite3
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.getenv("DATABASE_NAME", "tasks.db")
DB_PATH = os.path.join(BASE_DIR, DB_NAME)


def get_connection():
    """
    Establish a connection to the SQLite database.
    Uses DB_PATH defined by environment variables.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialize the database and create the tasks table if it doesn't exist.
    """
    with get_connection() as conn:
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    circuit TEXT,
                    status TEXT,
                    result TEXT,
                    error TEXT
                )
            """)
            # English print statement as per instructions
            print(f"Database initialized at: {DB_PATH}")
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")


def create_task(circuit_data: str) -> str:
    """
    Insert a new task into the database with a unique UUID.
    """
    task_id = str(uuid.uuid4())
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO tasks (id, circuit, status) VALUES (?, ?, ?)",
                (task_id, circuit_data, "submitted")
            )
            return task_id
    except sqlite3.Error as e:
        print(f"Error creating task {task_id}: {e}")
        raise


def get_task_by_id(task_id: str):
    """
    Fetch task details by ID and return as a dictionary.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, result, error FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Database error while fetching task {task_id}: {e}")
        raise
