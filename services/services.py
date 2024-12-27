import sqlite3
from datetime import datetime, timedelta
import random

WORKDAY_DURATION_MINUTES = 8 * 60 + 30  # 510 минут

def start_record():
    conn = sqlite3.connect('data/attendance.db')
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
    conn = sqlite3.connect('data/attendance.db')
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
    conn = sqlite3.connect('data/attendance.db')
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
    conn = sqlite3.connect('data/attendance.db')
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
    conn = sqlite3.connect('data/attendance.db')
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


def get_random_sticker(sticker_list):
    return random.choice(sticker_list)

# Обработка добавления записи вручную
def add_manual_entry(user_id, date_str, arrival_str, departure_str):
    # Парсим дату и время
    try:
        arrival_time = datetime.strptime(f"{date_str} {arrival_str}", "%Y-%m-%d %H:%M:%S")
        departure_time = datetime.strptime(f"{date_str} {departure_str}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return "Неверный формат даты или времени. Используйте формат: Y-m-d H:M:S"
    # Определяем дату без времени
    arrival_date = arrival_time.date()
    # Добавляем запись в базу данных
    conn = sqlite3.connect('data/attendance.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM attendance
        WHERE user_id = ? AND arrival_date = ?
    ''', (user_id, arrival_date))
    existing_record = cursor.fetchone()
    
    if existing_record:
        # Обновляем запись
        cursor.execute('''
            UPDATE attendance
            SET arrival_time = ?, departure_time = ?
            WHERE id = ?
        ''', (arrival_time.strftime('%Y-%m-%d %H:%M:%S'),
              departure_time.strftime('%Y-%m-%d %H:%M:%S'),
              existing_record[0]))
        conn.commit()
        conn.close()
        return "Запись обновлена!"
    else:
        # Добавляем новую запись
        cursor.execute('''
            INSERT INTO attendance (user_id, arrival_time, departure_time, arrival_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id,
              arrival_time.strftime('%Y-%m-%d %H:%M:%S'),
              departure_time.strftime('%Y-%m-%d %H:%M:%S'),
              arrival_date))
        conn.commit()
        conn.close()
        return "Запись успешно добавлена!"
 
def get_monthly_records(user_id):
    conn = sqlite3.connect('data/attendance.db')
    cursor = conn.cursor()
    
    # Определяем начало и конец текущего месяца
    now = datetime.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    
    # Получаем записи о приходе и уходе за текущий месяц
    cursor.execute('''
        SELECT arrival_time, departure_time FROM attendance
        WHERE user_id = ? AND
              arrival_time BETWEEN ? AND ? AND
              departure_time IS NOT NULL
    ''', (user_id, start_of_month, end_of_month))
    
    records = cursor.fetchall()
    conn.close()
    return records
def calculate_monthly_balance(user_id):
    records = get_monthly_records(user_id)
    total_minutes = 0  # Суммарное количество отработанных минут
    
    for arrival_str, departure_str in records:
        arrival_time = datetime.strptime(arrival_str, '%Y-%m-%d %H:%M:%S')
        departure_time = datetime.strptime(departure_str, '%Y-%m-%d %H:%M:%S')
        
        # Вычисляем количество минут, отработанных за день
        work_duration = (departure_time - arrival_time).total_seconds() / 60  # в минутах
        total_minutes += work_duration - WORKDAY_DURATION_MINUTES  # Разница с нормой
    
    # Переводим минуты в часы и минуты
    hours, minutes = divmod(int(total_minutes), 60)
    
    if total_minutes > 0:
        return f"Переработка в этом месяце: {hours} часов {minutes} минут"
    elif total_minutes < 0:
        return f"Недоработка в этом месяце: {abs(hours)} часов {abs(minutes)} минут"
    else:
        return "Все отработано в точности по графику!"
    
def reload_table():
   conn = sqlite3.connect('data/attendance.db')
   cursor = conn.cursor()
   cursor.execute(''' UPDATE attendance SET arrival_date = DATE(arrival_time)''')
   conn.commit()
   conn.close()
   return "База обновлена!"