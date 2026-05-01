import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats
from config_data.config import Config, load_config
from handlers import admin_handlers, other_handlers, user_handlers
from services.admin_service import AdminService
from services.attendance_service import AttendanceService

# logger
logger = logging.getLogger(__name__)


async def setup_bot_commands(bot: Bot):
    private_commands = [
        BotCommand(command='start', description='Запустить бота'),
        BotCommand(command='help', description='Справка'),
        BotCommand(command='in', description='Отметить приход'),
        BotCommand(command='out', description='Отметить уход'),
        BotCommand(command='week', description='Статистика за неделю'),
        BotCommand(command='month', description='Статистика за месяц'),
        BotCommand(command='balance', description='Баланс времени'),
        BotCommand(command='all_stats', description='Вся статистика'),
    ]
    group_commands = [
        BotCommand(command='setup_chat', description='Включить бота в этом чате'),
        BotCommand(command='chat_info', description='Информация о чате'),
        BotCommand(command='chat_admins', description='Админы бота в чате'),
        BotCommand(command='add_admin', description='Добавить админа чата'),
        BotCommand(command='remove_admin', description='Удалить админа чата'),
        BotCommand(command='disable_chat', description='Отключить бота в чате'),
        BotCommand(command='in', description='Отметить приход'),
        BotCommand(command='out', description='Отметить уход'),
        BotCommand(command='week', description='Статистика за неделю'),
        BotCommand(command='month', description='Статистика за месяц'),
        BotCommand(command='balance', description='Баланс времени'),
    ]
    await bot.set_my_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())


# bot start
async def main():
    # log configs
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d -8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # display the bot start
    logger.info('Starting bot')

    # load configurations to config
    config: Config = load_config()
    AttendanceService.initialize_db()
    AdminService.initialize_db()

    # bot and dispatcher
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # register routers
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    # run polling
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_bot_commands(bot)
    await dp.start_polling(bot)


asyncio.run(main())
