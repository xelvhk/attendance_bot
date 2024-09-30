from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from keyboards.keyboards import yatut_kb
from lexicon.lexicon_ru import LEXICON_RU
from services.services import record_arrival, record_departure, start_record, get_week_stats, get_month_stats, format_stats, record_manual_hours, clear_user_stats

router = Router()
bot = Bot

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

@router.message(F.text.in_([LEXICON_RU['answers']['netut']]))
async def departed(message: Message):
    user_id = message.from_user.id
    record_departure(user_id)
    await message.reply("Отметили время ухода!")

# Обработчик нажатия на кнопку "МК"
@router.message(F.text.in_([LEXICON_RU['answers']['mk']]))
async def manual_hours(message: Message):
    user_id = message.from_user.id
    record_manual_hours(user_id)
    await message.reply("Записаны фиксированные 8.5 часов рабочего дня.")

@router.message(F.text.in_([LEXICON_RU['week']]))
async def week_stats(message: Message):
    user_id = message.from_user.id
    records = get_week_stats(user_id)
    formatted_stats = format_stats(records)  # Отформатированная запись
    await message.reply(formatted_stats)

# Обработчик нажатия на кнопку "Статистика за месяц"
@router.message(F.text.in_([LEXICON_RU['month']]))
async def month_stats(message: Message):
    user_id = message.from_user.id
    records = get_month_stats(user_id)
    formatted_stats = format_stats(records)  # Отформатированная запись
    await message.reply(formatted_stats)

# Обработчик для кнопки "Стереть статистику"
@router.message(F.text.in_([LEXICON_RU['clear_stats']]))
async def clear_stats(message: Message):
    user_id = message.from_user.id
    clear_user_stats(user_id)  # Вызываем функцию очистки данных
    await message.reply("Ваша статистика успешно стерта.")

# Обработчик для КНОПОЧКИ
@router.message(F.text.in_([LEXICON_RU['knop']]))
async def clear_stats(message: Message):
    await message.reply("Хуёбочка! Нажми на кнопульку, а не напиши, идиот!")