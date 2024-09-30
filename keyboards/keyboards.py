from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from lexicon.lexicon_ru import LEXICON_RU


# Создаем кнопки клавиатуры
yatut_button_1 = KeyboardButton(text=LEXICON_RU['answers']['tut'])
yatut_button_2 = KeyboardButton(text=LEXICON_RU['answers']['netut'])

# Создаем клавиатуру функций
yatut_kb = ReplyKeyboardMarkup(
    keyboard=[[yatut_button_1],
              [yatut_button_2]],
    resize_keyboard=True
)
