import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from aiogram.client.default import DefaultBotProperties

from settings import BOT_TOKEN, MANAGER_CHAT_ID, WEBAPP_URL
from api_service import set_bot_instance
from app.start import start_router
from admin import admin_router

main_router = Router()

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


def get_web_app_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    web_app_info = WebAppInfo(url=WEBAPP_URL)

    builder.button(
        text="🛍️ Перейти в Каталог Periphery",
        web_app=web_app_info
    )

    return builder.as_markup()


def initiate_bot() -> tuple[Bot, Dispatcher]:
    if not BOT_TOKEN:
        logger.error("🛑 ОШИБКА: Токен BOT_TOKEN не найден. Проверьте .env файл.")
        raise ValueError("BOT_TOKEN is not set.")

    if not MANAGER_CHAT_ID:
        logger.error("🛑 ОШИБКА: ID менеджера MANAGER_CHAT_ID не установлен. Проверьте .env.")
        raise ValueError("MANAGER_CHAT_ID is not set.")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    set_bot_instance(bot, MANAGER_CHAT_ID)

    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(main_router)


    return bot, dp


async def main():
    try:
        bot, dp = initiate_bot()

        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("🤖 Бот запущен и готов к работе в режиме Polling...")
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