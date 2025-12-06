import json
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from settings import WEBAPP_URL, BOT_TOKEN

logger = logging.getLogger(__name__)

router = Router()


class UserForm(StatesGroup):
    waiting_for_web_app_data = State()


@router.message(F.text == "/start")
async def command_start_handler(message: Message) -> None:

    web_app_url = WEBAPP_URL
    web_app_info = WebAppInfo(url=web_app_url)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Перейти в Web App", web_app=web_app_info)]
    ])

    await message.answer("Добро пожаловать! Нажмите кнопку ниже, чтобы открыть наше Web App:", reply_markup=keyboard)


def initialize_bot() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    return bot, dp