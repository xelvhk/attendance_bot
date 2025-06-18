from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from lexicon.lexicon_ru import LEXICON_RU


# Создаем кнопки клавиатуры
yatut_button_1 = KeyboardButton(text=LEXICON_RU['answers']['tut'])
yatut_button_2 = KeyboardButton(text=LEXICON_RU['answers']['netut'])
yatut_button_3 = KeyboardButton(text=LEXICON_RU['answers']['mk'])
yatut_button_4 = KeyboardButton(text=LEXICON_RU['answers']['uvc'])
yatut_button_5 = KeyboardButton(text=LEXICON_RU['answers']['uvs'])
yatut_button_6 = KeyboardButton(text=LEXICON_RU['answers']['holidays'])
yatut_button_7 = KeyboardButton(text=LEXICON_RU['answers']['one_day'])
yatut_button_8 = KeyboardButton(text=LEXICON_RU['answers']['short_day'])
yatut_button_9 = KeyboardButton(text=LEXICON_RU['print'])
yatut_button_10 = KeyboardButton(text=LEXICON_RU['check_time'])
yatut_button_11 = KeyboardButton(text=LEXICON_RU['week'])
yatut_button_12 = KeyboardButton(text=LEXICON_RU['month'])
yatut_button_13 = KeyboardButton(text=LEXICON_RU['all_records'])

# Создаем клавиатуру функций
yatut_kb = ReplyKeyboardMarkup(
    keyboard=[[yatut_button_1],
              [yatut_button_2],
              [yatut_button_3],
              [yatut_button_4],
              [yatut_button_5],
              [yatut_button_6],
              [yatut_button_7],
              [yatut_button_8],
              [yatut_button_9],
              [yatut_button_10],
              [yatut_button_11],
              [yatut_button_12],
              [yatut_button_13],              
              ],
    resize_keyboard=True
)
