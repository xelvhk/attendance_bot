import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import other_handlers, user_handlers

# logger
logger = logging.getLogger(__name__)


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

    # bot and dispatcher
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # register routers
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    # run polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
