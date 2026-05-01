import sqlite3

from environs import Env

env = Env()
env.read_env()
DB_PATH = env.str('DB_PATH', 'attendance.db')


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
