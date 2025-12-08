import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from settings import BOT_TOKEN, MANAGER_CHAT_ID
from api_service import set_bot_instance

from app.main_handlers import router as main_router
from app.menu_handlers import router as menu_router
from app.order_handlers import router as order_router
from admin import admin_router

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


def initiate_bot() -> tuple[Bot, Dispatcher]:
    """
    """
    if not BOT_TOKEN:
        logger.error("🛑 ОШИБКА: Токен BOT_TOKEN не найден. Проверьте .env файл.")
        raise ValueError("BOT_TOKEN is not set.")

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    set_bot_instance(bot, MANAGER_CHAT_ID)

    dp.include_router(admin_router)
    dp.include_router(order_router)
    dp.include_router(main_router)
    dp.include_router(menu_router)

    return bot, dp


async def main():
    try:
        bot, dp = initiate_bot()
        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("🤖 Бот запущен и готов к работе...")
        await dp.start_polling(bot)
    except ValueError as e:
        logger.critical(f"🛑 Критическая ошибка инициализации: {e}")
    except Exception as e:
        logger.critical(f"🛑 Критическая ошибка при запуске бота: {e}")
    finally:
        if 'bot' in locals() and bot is not None:
            await bot.session.close()
            logger.info("Сессия бота закрыта.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("❌ Бот остановлен вручную.")