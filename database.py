import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "school_bus.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Parent'
        )
    """)

    # Buses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            bus_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_number TEXT NOT NULL,
            driver_name TEXT,
            route_name TEXT,
            status TEXT DEFAULT 'Waiting',
            latitude REAL,
            longitude REAL
        )
    """)

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_code TEXT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            bus_id INTEGER,
            stop_name TEXT NOT NULL,
            FOREIGN KEY (parent_id) REFERENCES users(user_id),
            FOREIGN KEY (bus_id) REFERENCES buses(bus_id)
        )
    """)

    # Bus location history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bus_locations (
            location_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_id INTEGER NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            speed REAL DEFAULT 0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bus_id) REFERENCES buses(bus_id)
        )
    """)

    # Upgrade existing students table safely
    student_columns = {
        row["name"]
        for row in cursor.execute(
            "PRAGMA table_info(students)"
        ).fetchall()
    }

    if "student_code" not in student_columns:
        cursor.execute(
            "ALTER TABLE students ADD COLUMN student_code TEXT"
        )

    # Upgrade existing buses table safely
    bus_columns = {
        row["name"]
        for row in cursor.execute(
            "PRAGMA table_info(buses)"
        ).fetchall()
    }

    if "latitude" not in bus_columns:
        cursor.execute("ALTER TABLE buses ADD COLUMN latitude REAL")

    if "longitude" not in bus_columns:
        cursor.execute("ALTER TABLE buses ADD COLUMN longitude REAL")

    if "status" not in bus_columns:
        cursor.execute(
            "ALTER TABLE buses ADD COLUMN status TEXT DEFAULT 'Waiting'"
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")
