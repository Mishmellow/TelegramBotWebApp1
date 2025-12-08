import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder

from settings import WEBHOOK_HOST
from app.keyboard import inline_category_keyboard, back_to_main_keyboard

logger = logging.getLogger(__name__)

router = Router()
WEB_APP_URL = f"{WEBHOOK_HOST}/webapp/index.html"


def get_combined_start_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    web_app_info = WebAppInfo(url=WEB_APP_URL)
    builder.row(
        InlineKeyboardButton(
            text="🛍️ Открыть Каталог",
            web_app=web_app_info
        )
    )

    existing_markup = inline_category_keyboard().inline_keyboard
    for row in existing_markup:
        builder.row(*row)

    return builder.as_markup()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    keyboard = get_combined_start_keyboard()

    await message.answer(
        f"Привет, {message.from_user.full_name}! Добро пожаловать! Выберите раздел:",
        reply_markup=keyboard
    )

@router.callback_query(F.data == 'about_us')
async def handle_about_us(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        'ℹ️ Мы - команда Periphery, создающая лучшие решения...',
        reply_markup=back_to_main_keyboard()
    )