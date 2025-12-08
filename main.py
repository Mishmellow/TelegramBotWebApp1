# main.py (Файл запуска Polling)
import logging
import asyncio
from aiogram import Bot, Dispatcher

from settings import BOT_TOKEN, MANAGER_CHAT_ID
from api_service import set_bot_instance

from admin import admin_router
# ⬅️ ИМПОРТИРУЕМ ИЗ ТОЛЬКО ЧТО СОЗДАННОГО ФАЙЛА
from app.menu_handlers import router as main_router
from app.order_handlers import router as client_router

logger = logging.getLogger(__name__)


def initiate_bot() -> tuple[Bot, Dispatcher]:

    if not BOT_TOKEN:
        logger.error("🛑 ОШИБКА: Токен BOT_TOKEN не найден.")
        raise ValueError("BOT_TOKEN is not set.")

    bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
    dp = Dispatcher()

    dp.include_router(main_router)  # <-- Теперь это наш роутер с /start
    dp.include_router(client_router)
    dp.include_router(admin_router)

    set_bot_instance(bot, MANAGER_CHAT_ID)

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
        if 'bot' in locals():
            await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("❌ Бот остановлен вручную.")