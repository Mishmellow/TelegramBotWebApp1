import logging
from aiogram import Router
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

from settings import WEBAPP_URL

logger = logging.getLogger(__name__)

start_router = Router()

@start_router.message(CommandStart())
async def start_handler(message: Message) -> None:
    web_app_url = WEBAPP_URL

    web_app_info = WebAppInfo(url=web_app_url)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Перейти в Каталог", callback_data="catalog_main")],
        [InlineKeyboardButton(text="ℹ️ О нас / Контакты", callback_data="info_contacts")],
        [InlineKeyboardButton(text="🚀 Перейти в Web App", web_app=web_app_info)]
    ])

    await message.answer("Добро пожаловать! Выберите интересующий раздел:", reply_markup=keyboard)