import sqlite3
from datetime import datetime, timedelta

def start_record():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        arrival_time TEXT,
        departure_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Функция для записи прихода в базу данных
def record_arrival(user_id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Записываем время прихода
    cursor.execute('''
        INSERT INTO attendance (user_id, arrival_time)
        VALUES (?, ?)
    ''', (user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

# Функция для записи ухода в базу данных
def record_departure(user_id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Обновляем время ухода для последней записи времени прихода
    cursor.execute('''
        UPDATE attendance
        SET departure_time = ?
        WHERE user_id = ? AND departure_time IS NULL
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))

    conn.commit()
    conn.close()

# Функция для получения статистики за последние N дней
def get_stats(user_id, days):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Рассчитываем дату, начиная с которой нужно брать данные
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

    # SQL-запрос для получения записей за последние N дней
    cursor.execute('''
        SELECT arrival_time, departure_time 
        FROM attendance
        WHERE user_id = ? AND arrival_time >= ?
        ORDER BY arrival_time
    ''', (user_id, start_date))

    records = cursor.fetchall()
    conn.close()

    return records

# Функция для форматирования и отправки статистики
def format_stats(records):
    if not records:
        return "Записей за указанный период нет."

    response = "Статистика за указанный период:\n"
    for arrival, departure in records:
        response += f"Приход: {arrival}, Уход: {departure or 'не указан'}\n"

    return response