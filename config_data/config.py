from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_ids: list[int]


@dataclass
class Config:
    tg_bot: TgBot
    db_path: str


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    admin_ids_raw = env.list('ADMIN_IDS', default=[])
    admin_ids = [int(admin_id) for admin_id in admin_ids_raw if str(admin_id).strip()]
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=admin_ids,
        ),
        db_path=env.str('DB_PATH', 'attendance.db'),
    )
