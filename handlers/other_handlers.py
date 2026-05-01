from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON_RU

router = Router()

# handler for non-typical requests
@router.message(F.chat.type == ChatType.PRIVATE)
async def send_answer(message: Message):
    await message.answer(text=LEXICON_RU['other_answer'])
