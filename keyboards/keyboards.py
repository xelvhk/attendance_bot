from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from lexicon.lexicon_ru import LEXICON_RU


# Создаем кнопки клавиатуры
yatut_button_1 = KeyboardButton(text=LEXICON_RU['answers']['tut'])
yatut_button_2 = KeyboardButton(text=LEXICON_RU['answers']['netut'])
yatut_button_3 = KeyboardButton(text=LEXICON_RU['answers']['mk'])
yatut_button_4 = KeyboardButton(text=LEXICON_RU['print'])
yatut_button_5 = KeyboardButton(text=LEXICON_RU['check_time'])
yatut_button_6 = KeyboardButton(text=LEXICON_RU['week'])
yatut_button_7 = KeyboardButton(text=LEXICON_RU['month'])
yatut_button_8 = KeyboardButton(text=LEXICON_RU['clear_stats'])

# Создаем клавиатуру функций
yatut_kb = ReplyKeyboardMarkup(
    keyboard=[[yatut_button_1],
              [yatut_button_2],
              [yatut_button_3],
              [yatut_button_4],
              [yatut_button_5],
              [yatut_button_6],
              [yatut_button_7],
              [yatut_button_8]
              ],
    resize_keyboard=True
)
