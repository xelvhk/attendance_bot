import sqlite3
from datetime import datetime, timedelta,timezone
import random

WORKDAY_DURATION_MINUTES = 8 * 60 + 30  # 510 минут
SPB = timezone(timedelta(hours=3))
def start_record():
    conn = sqlite3.connect('/data/attendance.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        arrival_time TEXT,
        departure_time TEXT,
        status TEXT DEFAULT NULL,
        custom_duration_minutes INTEGER DEFAULT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Функция для записи прихода в базу данных
def record_arrival(user_id):
    conn = sqlite3.connect('/data/attendance.db')
    cursor = conn.cursor()

    # Записываем время прихода
    cursor.execute('''
        INSERT INTO attendance (user_id, arrival_time)
        VALUES (?, ?)
    ''', (user_id, datetime.now(SPB).strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

# Функция для записи ухода в базу данных
def record_departure(user_id):
    conn = sqlite3.connect('/data/attendance.db')
    cursor = conn.cursor()

    # Обновляем время ухода для последней записи времени прихода
    cursor.execute('''
        UPDATE attendance
        SET departure_time = ?
        WHERE user_id = ? AND departure_time IS NULL
    ''', (datetime.now(SPB).strftime('%Y-%m-%d %H:%M:%S'), user_id))

    conn.commit()
    conn.close()

# Функция для получения статистики за последние N дней
def get_stats(user_id, mode):
    now = datetime.now()
    today = now.date()

    if mode == "week":
        start = today - timedelta(days=today.weekday())  # понедельник
    elif mode == "month":
        start = today.replace(day=1)  # первое число месяца
    else:
        raise ValueError("mode must be 'week' or 'month'")

    conn = sqlite3.connect("/data/attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT arrival_time, departure_time, status, custom_duration_minutes
        FROM attendance
        WHERE user_id = ?
        AND DATE(COALESCE(arrival_time, departure_time)) >= ?
        ORDER BY COALESCE(arrival_time, departure_time)
    """, (user_id, start.isoformat()))

    data = cursor.fetchall()
    conn.close()
    return data


# Функция для форматирования статистики с расчетом разницы во времени
def format_stats(data):
    from datetime import datetime, timedelta
    from collections import OrderedDict

    SPB = timedelta(hours=3)
    result = ""
    total_time = timedelta()
    days_counted = set()

    records_by_day = OrderedDict()

    emoji_map = {
        'Отпуск': '🏖',
        'Свой счёт': '💸',
        'УВЦ': '🛑',
        'УВС': '⏳',
        'короткий': '⏳'
    }

    for arrival_str, departure_str, status, custom_minutes in data:
        try:
            if arrival_str:
                day = (datetime.fromisoformat(arrival_str) + SPB).date()
            elif departure_str:
                day = (datetime.fromisoformat(departure_str) + SPB).date()
            else:
                continue
        except:
            continue

        # 🏷 Статусные записи
        if status in emoji_map:
            display = f"{emoji_map[status]} {status}"
            duration = timedelta(minutes=custom_minutes) if custom_minutes else None
            records_by_day[day] = (display, duration)
            if duration:
                total_time += duration
                days_counted.add(day)
            continue

        # 🕒 Вручную с duration
        if custom_minutes:
            duration = timedelta(minutes=int(custom_minutes))
            display = f"{emoji_map.get(status, '⏳')} {duration} (вручную)"
            records_by_day[day] = (display, duration)
            total_time += duration
            days_counted.add(day)
            continue

        # ✅ Стандартный приход/уход
        if arrival_str and departure_str:
            try:
                arrival = datetime.fromisoformat(arrival_str) + SPB
                departure = datetime.fromisoformat(departure_str) + SPB
                duration = departure - arrival
                records_by_day[day] = (str(duration), duration)
                total_time += duration
                days_counted.add(day)
            except:
                continue

    for day, (display, duration) in records_by_day.items():
        result += f"{day.strftime('%d.%m.%Y')}: {display}\n"

    expected_time = timedelta(hours=8, minutes=30) * len(days_counted)
    delta = total_time - expected_time

    result += f"\n<b>Всего: {total_time} / Ожидалось: {expected_time}</b>\n"
    if delta.total_seconds() > 0:
        result += f"✅ Переработка: {delta}\n"
    elif delta.total_seconds() < 0:
        result += f"⚠️ Недоработка: {-delta}\n"
    else:
        result += "✅ Всё точно по плану!\n"

    return result

# Функция для записи 8.5 часов рабочего дня в базу данных
def record_manual_hours(user_id):
    conn = sqlite3.connect('/data/attendance.db')
    cursor = conn.cursor()
    # Текущее время для прихода
    arrival_time = datetime.now(SPB)
    # Рассчитываем фиксированное время ухода (через 8.5 часов после прихода)
    departure_time = arrival_time + timedelta(hours=8, minutes=30)
    cursor.execute("""
        DELETE FROM attendance
        WHERE user_id = ? AND DATE(COALESCE(arrival_time, departure_time)) = ?
        """, (user_id, arrival_time.date()))
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
    # Добавляем запись в базу данных
    conn = sqlite3.connect('/data/attendance.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM attendance
        WHERE user_id = ? AND arrival_time = ?
    ''', (user_id, arrival_time))
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
            INSERT INTO attendance (user_id, arrival_time, departure_time)
            VALUES (?, ?, ?)
        ''', (user_id,
              arrival_time.strftime('%Y-%m-%d %H:%M:%S'),
              departure_time.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        return "Запись успешно добавлена!"
 
def get_monthly_records(user_id):
    conn = sqlite3.connect('/data/attendance.db')
    cursor = conn.cursor()
    
    # Определяем начало и конец текущего месяца
    now = datetime.now(SPB)
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