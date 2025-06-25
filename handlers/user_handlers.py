from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from datetime import datetime, timedelta, timezone
import re
from keyboards.keyboards import yatut_kb
from lexicon.lexicon_ru import LEXICON_RU
from services.attendance_service import AttendanceService
from services.stats_service import StatsService
from services.config_services import SPB, WORK_STATUSES
from services.util import get_random_sticker

# NOTE: All comments are now in english not russian :(
router = Router()
# ID стикеров
STICKER_ARRIVED = ['CAACAgIAAxkBAAEI3cFm-wxyyOtvqI94tfrsref6_vwaFQACgQADBL0eGX0AATUSNQ505jYE',
                   'CAACAgIAAxkBAAEI3b9m-wwZr8UwSWMVmiBBLc8UMcOOeAACUQADaJpdDO_0j_QyLokTNgQ',
                   'CAACAgIAAxkBAAEI9AZm__ihfUi2-LBZdFiVzda0IY4PngACFQADaJpdDHRGO4k8qzJQNgQ',
                   'CAACAgIAAxkBAAEI9Ahm__kM-5T1cpLhW0iuOY2MG-Ih6gACCQIAApmYRhHu7C34bJoF1TYE',
                   'CAACAgIAAxkBAAEI9Apm__k5sV9yawtbXHuHm-rlNV-r2QACwAADaJpdDGzvGdYfOiFPNgQ',
                   'CAACAgIAAxkBAAEI9BBm__mLf4jgT_cV8CB_7kIHmufSsAACQhUAAvodeUsKTTuYgTFABjYE',
                   'CAACAgIAAxkBAAEI9BJm__m0Bkb2pucPPUJfj7Y_XNxsJQACURsAAh2yeUvKd43ZfiKSeDYE'
                   ]  # Random sticker "IN"
STICKER_DEPARTED = ['CAACAgIAAxkBAAEI3cNm-wylDrxF8qq1MRBSgZLjGrj65wACcQADBL0eGQ8rdMjS1JRXNgQ',
                    'CAACAgIAAxkBAAEI9BRm__naLKtp9G7kStDSLqXNZcaIQQACJwADaJpdDJBThnLCPeeYNgQ',
                    'CAACAgIAAxkBAAEI9BZm__nlqyfDLwrgC4kQFE4x_t6xkgACYgADaJpdDJ9PJNArZRlvNgQ',
                    'CAACAgIAAxkBAAEI9Bhm__ouLMBgRuHXoOf7ikmaW5xmHAAC-xoAAhoqIEoODNQzL8kL1TYE',
                    'CAACAgIAAxkBAAEI9Bxm__pAMKcvRwHjgrPVy-KFzuHAQQACfhUAAhMlGUnK7ezMNhIY0jYE',
                    'CAACAgIAAxkBAAEI9B5m__pPN56qnZMMoQLKf4VO-bfIMQAC7hIAArHhgUvaP9zgZv1VOTYE',
                    'CAACAgIAAxkBAAEI9CZm__skePjUlK_lOY4_U3fzk9Le4wACWwADBL0eGUCGJ_KiQaqKNgQ'
                    ] # Random sticker "OUT"
STICKER_MK = ['CAACAgIAAxkBAAEI3ctm-w96eM7IcAABjlqtItZEJu35ERIAAoAAA2iaXQykBJQoEKRMJzYE',
              'CAACAgIAAxkBAAEI9CJm__pxAQ_wnWgDitXQCXc8parULwAChgEAApmYRhF6rwotSDTotTYE',
              'CAACAgIAAxkBAAEI9CRm__qR-wAB5JwiRpr_G1Gv-68sXnkAArEAA2iaXQz-8JEfBeLuSDYE',
              'CAACAgIAAxkBAAEI9Cpm__tXELXoejI7Hx6CHf1kukqT4QACxzMAAln1gUhRishsNZeQlDYE',
              'CAACAgIAAxkBAAEI9C5m__uVk_4fo0_xkiQAAR3vUF8zK70AAgIBAAJWnb0KTuJsgctA5P82BA',
              'CAACAgIAAxkBAAEI9DBm__u8WmVrsYtmG2ySC5MElDR0IwACcQEAApmYRhGsKWEWWLL5djYE',
              'CAACAgIAAxkBAAEI9DJm__va-naeXrz0pL2jp3EhEdGLAgACVQADaJpdDPrD__zHs5XmNgQ'
              ] # Random sticker "MK"

# /start command handler
@router.message(CommandStart())
async def process_start_command(message: Message):
    AttendanceService.initialize_db()
    await message.answer(text=LEXICON_RU['/start'], reply_markup=yatut_kb)


# /help command handler
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

# handler for IN
@router.message(F.text.in_([LEXICON_RU['answers']['tut']]))
async def arrived(message: Message):
    user_id = message.from_user.id
    AttendanceService.record_arrival(user_id)
    await message.reply("Отметили время прихода!")
    await message.reply_sticker(get_random_sticker(STICKER_ARRIVED))

# handler for OUT
@router.message(F.text.in_([LEXICON_RU['answers']['netut']]))
async def departed(message: Message):
    user_id = message.from_user.id
    AttendanceService.record_departure(user_id)
    await message.reply("Отметили время ухода!")
    await message.reply_sticker(get_random_sticker(STICKER_DEPARTED))

# handler for "МК" button
@router.message(F.text.in_([LEXICON_RU['answers']['mk']]))
async def manual_hours(message: Message):
    user_id = message.from_user.id
    AttendanceService.add_manual_complete_day(user_id)
    await message.reply("Записаны фиксированные 8.5 часов рабочего дня.")
    await message.reply_sticker(get_random_sticker(STICKER_MK))

# handler for "UVC" button
@router.message(F.text.in_([LEXICON_RU['answers']['uvc']]))
async def full_leave(message: Message):
    user_id = message.from_user.id
    AttendanceService.add_status_record(user_id, WORK_STATUSES['FULL_LEAVE'])

    await message.answer("🟢 Увольнительная на день сохранена. Целый день без работы, ух!")
    await message.reply_sticker(get_random_sticker(STICKER_MK)) 

# handler for "UVS" button
@router.message(lambda message: message.text.lower().startswith("увс"))
async def short_leave(message: Message):
    user_id = message.from_user.id
    
    try:
        parts = message.text.strip().split()
        hours = float(parts[1])  # for example, "УВС 2"
        duration = int(hours * 60)
    except:
        await message.answer("Укажи сколько сегодня работал с увольнительной: например, 'УВС 6'")
        return

    AttendanceService.add_status_record(user_id, WORK_STATUSES['PARTIAL_LEAVE'], duration)

    await message.answer(f"🟠 Теперь отрабатывать {8.5-hours} ч.")
    await message.reply_sticker(get_random_sticker(STICKER_MK)) 



# handler for "За свой счёт" button
@router.message(F.text.in_([LEXICON_RU['answers']['one_day']]))
async def pay_day(message: Message):
    user_id = message.from_user.id
    AttendanceService.add_status_record(user_id, WORK_STATUSES['PERSONAL_DAY'])

    await message.answer("Минус зарплата :(")
    await message.reply_sticker(get_random_sticker(STICKER_MK))

# handler for "Укороченный" button
@router.message(lambda message: message.text.lower().startswith("укороченный"))
async def short_day(message: Message):
    user_id = message.from_user.id
    
    try:
        parts = message.text.strip().split()
        hours = float(parts[1])  # for example "укороченный 2"
        duration = int(hours * 60)
    except:
        await message.answer("Укажи сколько часов в итоге сегодня работаешь: например, 'укороченный 7'")
        return

    AttendanceService.add_status_record(user_id, WORK_STATUSES['SHORT_DAY'], duration)

    await message.answer(f"🟢 Укороченный день сохранён.")
    await message.reply_sticker(get_random_sticker(STICKER_MK)) 


# handler for "Отпуск" button
@router.message(F.text.in_([LEXICON_RU['answers']['holidays']]))
async def holiday(message: Message):
    user_id = message.from_user.id
    AttendanceService.add_status_record(user_id, WORK_STATUSES['VACATION'])

    await message.answer("Ура! Отпуск!")
    await message.reply_sticker(get_random_sticker(STICKER_MK)) 


@router.message(F.text.in_([LEXICON_RU['week']]))
async def week_stats(message: Message):
    user_id = message.from_user.id

    today = datetime.now(SPB)
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=4)          # Friday

    records = AttendanceService.get_period_records(user_id, start_of_week, end_of_week)
    result = StatsService.generate_week_stats(records)
    await message.answer(result, parse_mode='HTML')

# handler for "Статистика за месяц" button
@router.message(F.text.in_([LEXICON_RU['month']]))
async def month_stats(message: Message):
    user_id = message.from_user.id

    today = datetime.now(SPB)
    start_of_month = today.replace(day=1)

    records = AttendanceService.get_period_records(user_id, start_of_month)
    result = StatsService.generate_month_stats(records)
    await message.answer(result.strip(), parse_mode='HTML')

# your joke could be here
@router.message(F.text.in_([LEXICON_RU['knop']]))
async def just_pull(message: Message):
    await message.reply("Не пишем, а жмём")

pattern = r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})-(\d{2}:\d{2}:\d{2})"
@router.message(lambda message: re.match(pattern, message.text))
async def handle_manual_entry(message: Message):
    user_id = message.from_user.id
    match = re.match(pattern, message.text)
 
    if match:
        date_str = match.group(1)         # "yyyy-mm-dd"
        arrival_str = match.group(2)      # "hh:mm:ss"
        departure_str = match.group(3)    # "hh:mm:ss"
 
        response = AttendanceService.add_manual_entry(user_id, date_str, arrival_str, departure_str)
        await message.reply(response)
    else:
        await message.reply("Неверный формат. Используйте формат: yyyy-mm-dd hh:mm:ss-hh:mm:ss")

@router.message(F.text.in_([LEXICON_RU['print']]))
async def add_manual_stats(message: Message):
    await message.reply("Просто отправь мне сейчас в ответ предполагаемые дату и время в формате 2024-12-31 23:58:00-23:59:00")

@router.message(F.text.in_([LEXICON_RU['check_time']]))
async def handle_time_balance(message: Message):
    user_id = message.from_user.id
    records = AttendanceService.get_all_records(user_id)
    balance = StatsService.calculate_monthly_balance(records)
    await message.reply(balance)

@router.message(F.text.in_([LEXICON_RU['all_records']]))
async def show_full_statistics(message: Message):
    user_id = message.from_user.id
    
    records = AttendanceService.get_all_records(user_id)
    all_stats = StatsService.generate_all_stats(records)
    
    for result in all_stats:
        await message.answer(result, parse_mode='HTML')
