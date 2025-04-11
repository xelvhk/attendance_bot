from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from datetime import datetime
import sqlite3
import re
from keyboards.keyboards import yatut_kb
from lexicon.lexicon_ru import LEXICON_RU
from services.services import record_arrival, record_departure, start_record, get_stats, format_stats, record_manual_hours, get_random_sticker, add_manual_entry, calculate_monthly_balance
from datetime import timedelta
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

# Обработчик нажатий на кнопки
@router.message(F.text.in_([LEXICON_RU['answers']['tut']]))
async def arrived(message: Message):
    user_id = message.from_user.id
    record_arrival(user_id)
    await message.reply("Отметили время прихода!")
    await message.reply_sticker(get_random_sticker(STICKER_ARRIVED))

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

@router.message(F.text.in_([LEXICON_RU['week']]))
async def week_stats(message: Message):
    user_id = message.from_user.id
    records = get_stats(user_id, 7)
    response = format_stats(records)
    await message.reply(response)

# Обработчик нажатия на кнопку "Статистика за месяц"
@router.message(F.text.in_([LEXICON_RU['month']]))
async def month_stats(message: Message):
    user_id = message.from_user.id
    records = get_stats(user_id, 30)
    response = format_stats(records)
    await message.reply(response)

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
        SELECT arrival_time, departure_time
        FROM attendance
        WHERE user_id = ?
        ORDER BY arrival_time
    """, (user_id,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        await message.answer("Нет данных.")
        return

    monthly_data = defaultdict(list)

    for arrival_str, departure_str in data:
        # Преобразуем строки в datetime с учетом UTC+3
        arrival = datetime.fromisoformat(arrival_str) + SPB
        departure = datetime.fromisoformat(departure_str) + SPB
        month_key = arrival.strftime("%B %Y")
        worked_time = departure - arrival
        monthly_data[month_key].append((arrival.date(), worked_time))

    result = ""
    for month, records in monthly_data.items():
        result += f"\n<b>{month}</b>\n"
        total_time = timedelta()
        days_set = set()

        for day, worked in records:
            result += f"{day.strftime('%d.%m.%Y')}: {str(worked)}\n"
            total_time += worked
            days_set.add(day)

        expected_time = timedelta(hours=8, minutes=30) * len(days_set)
        delta = total_time - expected_time

        if delta.total_seconds() > 0:
            diff_str = f"✅ Переработка: {str(delta)}"
        elif delta.total_seconds() == 0:
            diff_str = f"✅ Всё нормально"
        else:
            diff_str = f"⚠️ Недоработка: {str(-delta)}"

        result += f"<b>Всего: {str(total_time)} — {diff_str}</b>\n"

    await message.answer(result, parse_mode='HTML')
