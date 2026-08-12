import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "school_bus.db"


def get_connection():

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()


    # =========================
    # USERS TABLE
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)


    # =========================
    # BUSES TABLE
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            bus_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_number TEXT UNIQUE NOT NULL,
            driver_name TEXT NOT NULL,
            route_name TEXT NOT NULL,
            status TEXT DEFAULT 'Stopped',
            latitude REAL DEFAULT 0,
            longitude REAL DEFAULT 0
        )
    """)


    # =========================
    # STUDENTS TABLE
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            bus_id INTEGER,
            stop_name TEXT NOT NULL,

            FOREIGN KEY(parent_id)
            REFERENCES users(user_id),

            FOREIGN KEY(bus_id)
            REFERENCES buses(bus_id)
        )
    """)


    # =========================
    # BUS LOCATIONS TABLE
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bus_locations (
            location_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_id INTEGER,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            speed REAL DEFAULT 0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(bus_id)
            REFERENCES buses(bus_id)
        )
    """)


    connection.commit()

    connection.close()


# =========================
# RUN DATABASE
# =========================

if __name__ == "__main__":

    initialize_database()

    print("Database initialized successfully.")