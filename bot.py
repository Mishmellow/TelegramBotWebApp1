import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo

from settings import BOT_TOKEN

bot_token = BOT_TOKEN

WEB_APP_URL = "http://127.0.0.1:8000/webapp.html"


def get_web_app_keyboard() -> types.InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    web_app_info = WebAppInfo(url=WEB_APP_URL)

    builder.button(
        text="🛍️ Перейти в Каталог Periphery",
        web_app=web_app_info
    )

    return builder.as_markup()


@asyncio.coroutine
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

    if bot_token == BOT_TOKEN:
        print("🛑 ОШИБКА: Пожалуйста, замени токен бота на реальный токен бота.")
        return

    bot = Bot(token=bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.message.register(start_handler, CommandStart())

    print("🚀 Бот запущен! Ищи его в Telegram...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())