from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from keyboards.keyboards import yatut_kb
from lexicon.lexicon_ru import LEXICON_RU
from services.services import record_arrival, record_departure, start_record, get_stats, format_stats, record_manual_hours, clear_user_stats

router = Router()
bot = Bot

# ID стикеров
STICKER_ARRIVED = 'CAACAgIAAxkBAAEI3cFm-wxyyOtvqI94tfrsref6_vwaFQACgQADBL0eGX0AATUSNQ505jYE'  # Стикер "Пришел"
STICKER_DEPARTED = 'CAACAgIAAxkBAAEI3cNm-wylDrxF8qq1MRBSgZLjGrj65wACcQADBL0eGQ8rdMjS1JRXNgQ'  # Стикер "Ушел"
STICKER_MK = 'CAACAgIAAxkBAAEI3ctm-w96eM7IcAABjlqtItZEJu35ERIAAoAAA2iaXQykBJQoEKRMJzYE' # Стикер "MK"

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
    await message.reply_sticker(STICKER_ARRIVED)

@router.message(F.text.in_([LEXICON_RU['answers']['netut']]))
async def departed(message: Message):
    user_id = message.from_user.id
    record_departure(user_id)
    await message.reply("Отметили время ухода!")
    await message.reply_sticker(STICKER_DEPARTED) 

# Обработчик нажатия на кнопку "МК"
@router.message(F.text.in_([LEXICON_RU['answers']['mk']]))
async def manual_hours(message: Message):
    user_id = message.from_user.id
    record_manual_hours(user_id)
    await message.reply("Записаны фиксированные 8.5 часов рабочего дня.")
    await message.reply_sticker(STICKER_MK) 

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