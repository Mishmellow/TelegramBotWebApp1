import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from aiogram.client.default import DefaultBotProperties

from settings import BOT_TOKEN, WEBHOOK_HOST, MANAGER_CHAT_ID
from api_service import set_bot_instance
from admin import admin_router


WEB_APP_URL = f"{WEBHOOK_HOST}/webapp/index.html"

logging.basicConfig(level=logging.INFO)


def get_web_app_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    web_app_info = WebAppInfo(url=WEB_APP_URL)

    builder.button(
        text="🛍️ Перейти в Каталог Periphery",
        web_app=web_app_info
    )

    return builder.as_markup()


async def start_handler(message: types.Message):
    markup = get_web_app_keyboard()

    welcome_text = (
        "Привет! 👋\n"
        "Добро пожаловать в каталог игрового оборудования Periphery.\n\n"
        "Нажми кнопку ниже, чтобы открыть наше Web App и выбрать товары."
    )

    await message.answer(
        text=welcome_text,
        reply_markup=markup
    )


async def main():
    
    if not BOT_TOKEN:
        print("🛑 ОШИБКА: Токен BOT_TOKEN не найден в переменных окружения. Проверьте файл .env.")
        return

    if not MANAGER_CHAT_ID:
        print("🛑 ОШИБКА: ID менеджера MANAGER_CHAT_ID не установлен. Проверьте файл .env.")
        return

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    set_bot_instance(bot, MANAGER_CHAT_ID)
    dp.include_router(admin_router)
    dp.message.register(start_handler, CommandStart())

    await bot.delete_webhook(drop_pending_updates=True)

    print("🚀 Бот запущен! Ищи его в Telegram...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())