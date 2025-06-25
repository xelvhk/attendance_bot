from datetime import datetime
import sqlite3

from .config_services import SPB, WORKDAY_DURATION_MINUTES

DB_PATH = '/data/attendance.db'


def connect_db():
    return sqlite3.connect(DB_PATH)


def execute_query(query, params=()):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()


def fetch_query(query, params=()):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
