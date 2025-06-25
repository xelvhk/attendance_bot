import random
from typing import List


def get_random_sticker(sticker_list: List[str]) -> str:
    """Возвращает рандомный стикер"""
    return random.choice(sticker_list)
