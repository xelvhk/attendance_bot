from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from datetime import datetime
import sqlite3
import re
from keyboards.keyboards import yatut_kb
from lexicon.lexicon_ru import LEXICON_RU
from services.services import record_arrival, record_departure, start_record, get_stats, format_stats, record_manual_hours, get_random_sticker, add_manual_entry, calculate_monthly_balance
from datetime import timedelta, timezone
from collections import defaultdict
router = Router()
bot = Bot
SPB = timedelta(hours=3)
# ID стикеров
STICKER_ARRIVED = ['CAACAgIAAxkBAAEI3cFm-wxyyOtvqI94tfrsref6_vwaFQACgQADBL0eGX0AATUSNQ505jYE',
                   'CAACAgIAAxkBAAEI3b9m-wwZr8UwSWMVmiBBLc8UMcOOeAACUQADaJpdDO_0j_QyLokTNgQ',
                   'CAACAgIAAxkBAAEI9AZm__ihfUi2-LBZdFiVzda0IY4PngACFQADaJpdDHRGO4k8qzJQNgQ',
                   'CAACAgIAAxkBAAEI9Ahm__kM-5T1cpLhW0iuOY2MG-Ih6gACCQIAApmYRhHu7C34bJoF1TYE',
                   'CAACAgIAAxkBAAEI9Apm__k5sV9yawtbXHuHm-rlNV-r2QACwAADaJpdDGzvGdYfOiFPNgQ',
                   'CAACAgIAAxkBAAEI9BBm__mLf4jgT_cV8CB_7kIHmufSsAACQhUAAvodeUsKTTuYgTFABjYE',
                   'CAACAgIAAxkBAAEI9BJm__m0Bkb2pucPPUJfj7Y_XNxsJQACURsAAh2yeUvKd43ZfiKSeDYE'
                   ]  # Случайный стикер "Пришел"
STICKER_DEPARTED = ['CAACAgIAAxkBAAEI3cNm-wylDrxF8qq1MRBSgZLjGrj65wACcQADBL0eGQ8rdMjS1JRXNgQ',
                    'CAACAgIAAxkBAAEI9BRm__naLKtp9G7kStDSLqXNZcaIQQACJwADaJpdDJBThnLCPeeYNgQ',
                    'CAACAgIAAxkBAAEI9BZm__nlqyfDLwrgC4kQFE4x_t6xkgACYgADaJpdDJ9PJNArZRlvNgQ',
                    'CAACAgIAAxkBAAEI9Bhm__ouLMBgRuHXoOf7ikmaW5xmHAAC-xoAAhoqIEoODNQzL8kL1TYE',
                    'CAACAgIAAxkBAAEI9Bxm__pAMKcvRwHjgrPVy-KFzuHAQQACfhUAAhMlGUnK7ezMNhIY0jYE',
                    'CAACAgIAAxkBAAEI9B5m__pPN56qnZMMoQLKf4VO-bfIMQAC7hIAArHhgUvaP9zgZv1VOTYE',
                    'CAACAgIAAxkBAAEI9CZm__skePjUlK_lOY4_U3fzk9Le4wACWwADBL0eGUCGJ_KiQaqKNgQ'
                    ] # Случайный стикер "Ушел"
STICKER_MK = ['CAACAgIAAxkBAAEI3ctm-w96eM7IcAABjlqtItZEJu35ERIAAoAAA2iaXQykBJQoEKRMJzYE',
              'CAACAgIAAxkBAAEI9CJm__pxAQ_wnWgDitXQCXc8parULwAChgEAApmYRhF6rwotSDTotTYE',
              'CAACAgIAAxkBAAEI9CRm__qR-wAB5JwiRpr_G1Gv-68sXnkAArEAA2iaXQz-8JEfBeLuSDYE',
              'CAACAgIAAxkBAAEI9Cpm__tXELXoejI7Hx6CHf1kukqT4QACxzMAAln1gUhRishsNZeQlDYE',
              'CAACAgIAAxkBAAEI9C5m__uVk_4fo0_xkiQAAR3vUF8zK70AAgIBAAJWnb0KTuJsgctA5P82BA',
              'CAACAgIAAxkBAAEI9DBm__u8WmVrsYtmG2ySC5MElDR0IwACcQEAApmYRhGsKWEWWLL5djYE',
              'CAACAgIAAxkBAAEI9DJm__va-naeXrz0pL2jp3EhEdGLAgACVQADaJpdDPrD__zHs5XmNgQ'
              ] # Случайный стикер "MK"

# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    start_record()
    await message.answer(text=LEXICON_RU['/start'],
                         reply_markup=yatut_kb)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

# Обработчик прихода
@router.message(F.text.in_([LEXICON_RU['answers']['tut']]))
async def arrived(message: Message):
    user_id = message.from_user.id
    record_arrival(user_id)
    await message.reply("Отметили время прихода!")
    await message.reply_sticker(get_random_sticker(STICKER_ARRIVED))

# Обработчик ухода
@router.message(F.text.in_([LEXICON_RU['answers']['netut']]))
async def departed(message: Message):
    user_id = message.from_user.id
    record_departure(user_id)
    await message.reply("Отметили время ухода!")
    await message.reply_sticker(get_random_sticker(STICKER_DEPARTED))

# Обработчик нажатия на кнопку "МК"
@router.message(F.text.in_([LEXICON_RU['answers']['mk']]))
async def manual_hours(message: Message):
    user_id = message.from_user.id
    record_manual_hours(user_id)
    await message.reply("Записаны фиксированные 8.5 часов рабочего дня.")
    await message.reply_sticker(get_random_sticker(STICKER_MK)) 

# Обработчик нажатия на кнопку "УВЦ"
@router.message(F.text.in_([LEXICON_RU['answers']['uvc']]))
async def full_leave(message: Message):
    user_id = message.from_user.id
    now = datetime.now(timezone(timedelta(hours=3)))

    conn = sqlite3.connect("/data/attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM attendance
    WHERE user_id = ? AND DATE(COALESCE(arrival_time, departure_time)) = ?
    """, (user_id, now.date()))

    cursor.execute("""
    INSERT INTO attendance (user_id, status, arrival_time)
    VALUES (?, ?, ?)
    """, (user_id, 'УВЦ', now.isoformat()))

    conn.commit()
    conn.close()

    await message.answer("🟢 Увольнительная на день сохранена. Целый день без работы, ух!")
    await message.reply_sticker(get_random_sticker(STICKER_MK)) 

# Обработчик нажатия на кнопку "УВC"
@router.message(lambda message: message.text.lower().startswith("увс"))
async def short_leave(message: Message):
    user_id = message.from_user.id
    now = datetime.now(timezone(timedelta(hours=3)))

    try:
        parts = message.text.strip().split()
        hours = float(parts[1])  # например, "УВС 2"
        duration = int(hours * 60)
    except:
        await message.answer("Укажи сколько сегодня работал с увольнительной: например, 'УВС 6'")
        return

    conn = sqlite3.connect("/data/attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM attendance
    WHERE user_id = ? AND DATE(COALESCE(arrival_time, departure_time)) = ?
    """, (user_id, now.date()))

    cursor.execute("""
    INSERT INTO attendance (user_id, status, custom_duration_minutes, arrival_time)
    VALUES (?, ?, ?, ?)
    """, (user_id, 'УВС', duration, now.isoformat()))

    conn.commit()
    conn.close()

    await message.answer(f"🟠 Теперь отрабатывать {8.5-hours} ч.")
    await message.reply_sticker(get_random_sticker(STICKER_MK)) 



# Обработчик нажатия на кнопку "За свой счёт"
@router.message(F.text.in_([LEXICON_RU['answers']['one_day']]))
async def pay_day(message: Message):
    user_id = message.from_user.id
    now = datetime.now(timezone(timedelta(hours=3)))

    conn = sqlite3.connect("/data/attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM attendance
    WHERE user_id = ? AND DATE(COALESCE(arrival_time, departure_time)) = ?
    """, (user_id, now.date()))

    cursor.execute("""
    INSERT INTO attendance (user_id, status, arrival_time)
    VALUES (?, ?, ?)
    """, (user_id, 'Свой счёт', now.isoformat()))

    conn.commit()
    conn.close()

    await message.answer("Минус зарплата :(")
    await message.reply_sticker(get_random_sticker(STICKER_MK))

# Обработчик нажатия на кнопку "Укороченный"
@router.message(lambda message: message.text.lower().startswith("укороченный"))
async def short_day(message: Message):
    user_id = message.from_user.id
    now = datetime.now(timezone(timedelta(hours=3)))

    try:
        parts = message.text.strip().split()
        hours = float(parts[1])  # например, "укороченный 2"
        duration = int(hours * 60)
    except:
        await message.answer("Укажи сколько часов в итоге сегодня работаешь: например, 'укороченный 7'")
        return

    conn = sqlite3.connect("/data/attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM attendance
    WHERE user_id = ? AND DATE(COALESCE(arrival_time, departure_time)) = ?
    """, (user_id, now.date()))

    cursor.execute("""
    INSERT INTO attendance (user_id, status, custom_duration_minutes, arrival_time)
    VALUES (?, ?, ?, ?)
    """, (user_id, 'короткий', duration, now.isoformat()))

    conn.commit()
    conn.close()

    await message.answer(f"🟢 Укороченный день сохранён.")
    await message.reply_sticker(get_random_sticker(STICKER_MK)) 


# Обработчик нажатия на кнопку "Отпуск"
@router.message(F.text.in_([LEXICON_RU['answers']['holidays']]))
async def holiday(message: Message):
    user_id = message.from_user.id
    now = datetime.now(timezone(timedelta(hours=3)))

    conn = sqlite3.connect("/data/attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM attendance
    WHERE user_id = ? AND DATE(COALESCE(arrival_time, departure_time)) = ?
    """, (user_id, now.date()))

    cursor.execute("""
    INSERT INTO attendance (user_id, status, arrival_time)
    VALUES (?, ?, ?)
    """, (user_id, 'Отпуск', now.isoformat()))

    conn.commit()
    conn.close()

    await message.answer("Ура! Отпуск!")
    await message.reply_sticker(get_random_sticker(STICKER_MK)) 


@router.message(F.text.in_([LEXICON_RU['week']]))
async def week_stats(message: Message):
    user_id = message.from_user.id

    today = datetime.now(timezone(SPB))
    start_of_week = today - timedelta(days=today.weekday())  # Понедельник
    end_of_week = start_of_week + timedelta(days=4)          # Пятница

    conn = sqlite3.connect("/data/attendance.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT arrival_time, departure_time, status, custom_duration_minutes
        FROM attendance
        WHERE user_id = ?
        AND DATE(COALESCE(arrival_time, departure_time)) BETWEEN ? AND ?
        ORDER BY COALESCE(arrival_time, departure_time)
    """, (user_id, start_of_week.date(), end_of_week.date()))
    data = cursor.fetchall()
    conn.close()

    if not data:
        await message.answer("Нет данных за эту неделю.")
        return

    result = "<b>📊 Рабочая неделя:</b>\n"
    total_work = timedelta()
    total_expected = timedelta()

    for arrival_str, departure_str, status, custom_duration in data:
        try:
            date = datetime.fromisoformat(arrival_str or departure_str) + SPB if arrival_str or departure_str else today
            day_str = date.strftime('%d.%m.%Y')

            if status in ['Отпуск', 'Свой счёт', 'УВЦ']:
                result += f"{day_str}: {status}\n"
                continue

            if status == 'короткий' and custom_duration:
                worked = timedelta(minutes=custom_duration)
                expected = worked
                total_work += worked
                total_expected += expected
                result += f"{day_str}: {str(worked)} (короткий)\n"
                continue

            if status == 'УВС' and custom_duration:
                # Отработал меньше обычного
                worked = timedelta(minutes=custom_duration)
                expected = timedelta(hours=8, minutes=30)
                total_work += worked
                total_expected += expected
                result += f"{day_str}: {str(worked)} (УВС)\n"
                continue

            if arrival_str and departure_str:
                arrival = datetime.fromisoformat(arrival_str) + SPB
                departure = datetime.fromisoformat(departure_str) + SPB
                worked = departure - arrival
                expected = timedelta(hours=8, minutes=30)
                total_work += worked
                total_expected += expected
                result += f"{arrival.date().strftime('%d.%m.%Y')}: {str(worked)}\n"

        except Exception as e:
            print(f"Ошибка при обработке: {e}")
            continue

    delta = total_work - total_expected
    if delta.total_seconds() > 0:
        result += f"\n<b>✅ Переработка за неделю: {str(delta)}</b>"
    elif delta.total_seconds() == 0:
        result += "\n<b>✅ Всё чётко</b>"
    else:
        result += f"\n<b>⚠️ Недоработка: {str(-delta)}</b>"

    await message.answer(result, parse_mode='HTML')

# Обработчик нажатия на кнопку "Статистика за месяц"
@router.message(F.text.in_([LEXICON_RU['month']]))
async def month_stats(message: Message):
    user_id = message.from_user.id

    today = datetime.now(timezone(SPB))
    start_of_month = today.replace(day=1)

    conn = sqlite3.connect("/data/attendance.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT arrival_time, departure_time, status, custom_duration_minutes
        FROM attendance
        WHERE user_id = ?
        AND DATE(COALESCE(arrival_time, departure_time)) >= ?
        ORDER BY COALESCE(arrival_time, departure_time)
    """, (user_id, start_of_month.date()))
    data = cursor.fetchall()
    conn.close()

    if not data:
        await message.answer("Нет данных за этот месяц.")
        return

    result = f"<b>📆 {today.strftime('%B %Y')}</b>\n"
    total_work = timedelta()
    total_expected = timedelta()

    for arrival_str, departure_str, status, custom_duration in data:
        try:
            date = datetime.fromisoformat(arrival_str or departure_str) + SPB if arrival_str or departure_str else today
            day_str = date.strftime('%d.%m.%Y')

            if status in ['Отпуск', 'Свой счёт', 'УВЦ']:
                result += f"{day_str}: {status}\n"
                continue

            if status == 'короткий' and custom_duration:
                worked = timedelta(minutes=custom_duration)
                expected = worked  # день укорочен, и отработано столько, сколько надо
                total_work += worked
                total_expected += expected
                result += f"{day_str}: {str(worked)} (короткий)\n"
                continue

            if status == 'УВС' and custom_duration:
                worked = timedelta(minutes=custom_duration)
                expected = timedelta(hours=8, minutes=30)  # норма остаётся прежней
                total_work += worked
                total_expected += expected
                result += f"{day_str}: {str(worked)} (УВС)\n"
                continue

            if arrival_str and departure_str:
                arrival = datetime.fromisoformat(arrival_str) + SPB
                departure = datetime.fromisoformat(departure_str) + SPB
                worked = departure - arrival
                expected = timedelta(hours=8, minutes=30)
                total_work += worked
                total_expected += expected
                result += f"{arrival.date().strftime('%d.%m.%Y')}: {str(worked)}\n"

        except Exception as e:
            print(f"Ошибка в месяце: {e}")
            continue

    delta = total_work - total_expected
    if delta.total_seconds() > 0:
        result += f"\n<b>✅ Переработка: {str(delta)}</b>"
    elif delta.total_seconds() == 0:
        result += "\n<b>✅ Всё чётко</b>"
    else:
        result += f"\n<b>⚠️ Недоработка: {str(-delta)}</b>"

    await message.answer(result.strip(), parse_mode='HTML')

# Обработчик для КНОПОЧКИ
@router.message(F.text.in_([LEXICON_RU['knop']]))
async def just_pull(message: Message):
    await message.reply("Не пишем, а жмём")

pattern = r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})-(\d{2}:\d{2}:\d{2})"
@router.message(lambda message: re.match(pattern, message.text))
async def handle_manual_entry(message: Message):
    user_id = message.from_user.id
    match = re.match(pattern, message.text)
 
    if match:
        date_str = match.group(1)         # "дд.мм"
        arrival_str = match.group(2)      # "чч:мм"
        departure_str = match.group(3)    # "чч:мм"
 
        response = add_manual_entry(user_id, date_str, arrival_str, departure_str)
        await message.reply(response)
    else:
        await message.reply("Неверный формат. Используйте формат: дд.мм чч:мм-чч:мм")

@router.message(F.text.in_([LEXICON_RU['print']]))
async def add_manual_stats(message: Message):
    await message.reply("Просто отправь мне сейчас в ответ предполагаемые дату и время в формате 2024-12-31 23:58:00-23:59:00")

@router.message(F.text.in_([LEXICON_RU['check_time']]))
async def handle_time_balance(message: Message):
    user_id = message.from_user.id
    balance = calculate_monthly_balance(user_id)
    await message.reply(balance)

@router.message(F.text.in_([LEXICON_RU['all_records']]))
async def show_full_statistics(message: Message):
    user_id = message.from_user.id

    conn = sqlite3.connect("/data/attendance.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT arrival_time, departure_time, status, custom_duration_minutes
        FROM attendance
        WHERE user_id = ?
        ORDER BY COALESCE(arrival_time, departure_time)
    """, (user_id,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        await message.answer("Нет данных.")
        return

    monthly_data = defaultdict(list)

    for arrival_str, departure_str, status, custom_duration in data:
        try:
            if status in ['Отпуск', 'Свой счёт', 'УВЦ']:
                date = datetime.fromisoformat(arrival_str or departure_str) + SPB if arrival_str or departure_str else datetime.now()
                month_key = date.strftime("%B %Y")
                monthly_data[month_key].append((date.date(), status, None, None))
                continue

            if status == 'короткий' and custom_duration:
                date = datetime.fromisoformat(arrival_str or departure_str) + SPB
                worked = timedelta(minutes=custom_duration)
                expected = worked  # норма тоже уменьшается
                month_key = date.strftime("%B %Y")
                monthly_data[month_key].append((date.date(), None, worked, expected))
                continue

            if status == 'УВС' and custom_duration:
                date = datetime.fromisoformat(arrival_str or departure_str) + SPB
                worked = timedelta(minutes=custom_duration)
                expected = timedelta(hours=8, minutes=30)  # норма не меняется
                month_key = date.strftime("%B %Y")
                monthly_data[month_key].append((date.date(), None, worked, expected))
                continue

            # Обычный рабочий день
            if arrival_str and departure_str:
                arrival = datetime.fromisoformat(arrival_str) + SPB
                departure = datetime.fromisoformat(departure_str) + SPB
                worked = departure - arrival
                expected = timedelta(hours=8, minutes=30)
                month_key = arrival.strftime("%B %Y")
                monthly_data[month_key].append((arrival.date(), None, worked, expected))

        except Exception as e:
            print(f"Ошибка при обработке записи: {e}")
            continue

    # Разделённая отправка по месяцам
    for month, records in monthly_data.items():
        result = f"<b>{month}</b>\n"
        total_work = timedelta()
        total_expected = timedelta()

        for day, status, worked, expected in records:
            if status:  # Статусный день
                result += f"{day.strftime('%d.%m.%Y')}: {status}\n"
            elif worked is not None:
                result += f"{day.strftime('%d.%m.%Y')}: {str(worked)}\n"
                total_work += worked
                total_expected += expected

        delta = total_work - total_expected
        if delta.total_seconds() > 0:
            result += f"<b>✅ Переработка: {str(delta)}</b>\n"
        elif delta.total_seconds() == 0:
            result += f"<b>✅ Всё отработано точно</b>\n"
        else:
            result += f"<b>⚠️ Недоработка: {str(-delta)}</b>\n"

        await message.answer(result.strip(), parse_mode='HTML')
