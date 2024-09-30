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

def get_current_workweek():
    today = datetime.now()
    # Начало недели (понедельник)
    start_of_week = today - timedelta(days=today.weekday())  # .weekday() возвращает 0 для понедельника
    # Конец недели (пятница)
    end_of_week = start_of_week + timedelta(days=4)
    return start_of_week, end_of_week

def get_current_month():
    today = datetime.now()
    # Первый день текущего месяца
    start_of_month = today.replace(day=1)
    # Последний день текущего месяца
    if today.month == 12:  # Если декабрь
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    return start_of_month, end_of_month

# Получаем статистику за текущую рабочую неделю
def get_week_stats(user_id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    start_of_week, end_of_week = get_current_workweek()
    cursor.execute('''
        SELECT arrival_time, departure_time 
        FROM attendance
        WHERE user_id = ? AND arrival_time >= ? AND arrival_time <= ?
        ORDER BY arrival_time
    ''', (user_id, start_of_week.strftime('%Y-%m-%d %H:%M:%S'), end_of_week.strftime('%Y-%m-%d %H:%M:%S')))
    records = cursor.fetchall()
    conn.close()
    return records

# Получаем статистику за текущий календарный месяц
def get_month_stats(user_id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    start_of_month, end_of_month = get_current_month()
    cursor.execute('''
        SELECT arrival_time, departure_time 
        FROM attendance
        WHERE user_id = ? AND arrival_time >= ? AND arrival_time <= ?
        ORDER BY arrival_time
    ''', (user_id, start_of_month.strftime('%Y-%m-%d %H:%M:%S'), end_of_month.strftime('%Y-%m-%d %H:%M:%S')))
    records = cursor.fetchall()
    conn.close()
    return records


# Функция для получения статистики за последние N дней
# def get_stats(user_id, days):
#     conn = sqlite3.connect('attendance.db')
#     cursor = conn.cursor()

#     # Рассчитываем дату, начиная с которой нужно брать данные
#     start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

#     # SQL-запрос для получения записей за последние N дней
#     cursor.execute('''
#         SELECT arrival_time, departure_time 
#         FROM attendance
#         WHERE user_id = ? AND arrival_time >= ?
#         ORDER BY arrival_time
#     ''', (user_id, start_date))

#     records = cursor.fetchall()
#     conn.close()

#     return records

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