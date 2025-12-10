import logging
from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from settings import WEBHOOK_HOST
from app.keyboard import inline_category_keyboard

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