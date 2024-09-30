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


# Функция для форматирования статистики с расчетом разницы во времени
def format_stats(records):
    if not records:
        return "Записей за указанный период нет."

    response = "Статистика за указанный период:\n"
    for arrival, departure in records:
        # Парсим время прихода и ухода из базы данных
        arrival_time = datetime.strptime(arrival, '%Y-%m-%d %H:%M:%S')
        
        if departure:
            departure_time = datetime.strptime(departure, '%Y-%m-%d %H:%M:%S')
            # Рассчитываем разницу во времени
            work_duration = departure_time - arrival_time
            hours, remainder = divmod(work_duration.total_seconds(), 3600)
            minutes = remainder // 60
            work_duration_str = f"{int(hours)} ч. {int(minutes)} мин."
        else:
            work_duration_str = 'Уход не зафиксирован'

        # Добавляем дату и рабочее время в ответ
        response += f"Дата: {arrival_time.strftime('%Y-%m-%d')}, Время на работе: {work_duration_str}\n"

    return response

# Функция для записи 8.5 часов рабочего дня в базу данных
def record_manual_hours(user_id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Текущее время для прихода
    arrival_time = datetime.now()
    # Рассчитываем фиксированное время ухода (через 8.5 часов после прихода)
    departure_time = arrival_time + timedelta(hours=8, minutes=30)

    # Записываем в базу данных с фиксированными 8.5 часами
    cursor.execute('''
        INSERT INTO attendance (user_id, arrival_time, departure_time)
        VALUES (?, ?, ?)
    ''', (user_id, arrival_time.strftime('%Y-%m-%d %H:%M:%S'), departure_time.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

    # Функция для удаления всех записей пользователя
def clear_user_stats(user_id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Удаляем все записи из таблицы attendance для данного пользователя
    cursor.execute('DELETE FROM attendance WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()