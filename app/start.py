import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, WebAppInfo, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup

from settings import WEBAPP_URL, BOT_TOKEN, MANAGER_CHAT_ID
from api_service import set_bot_instance
from admin import admin_router
from app.order_handlers import router as client_router
from app.keyboard import inline_category_keyboard


logger = logging.getLogger(__name__)

router = Router()


class UserForm(StatesGroup):
    waiting_for_web_app_data = State()


@router.message(F.text == "/start")
async def command_start_handler(message: Message) -> None:

    keyboard = inline_category_keyboard()

    web_app_url = WEBAPP_URL
    web_app_info = WebAppInfo(url=web_app_url)
    web_app_button = InlineKeyboardButton(text="🚀 Перейти в Web App", web_app=web_app_info)

    keyboard.inline_keyboard.append([web_app_button])

    await message.answer(
        "👋 Добро пожаловать! Выберите интересующий раздел:",
        reply_markup=keyboard
    )


def initiate_bot() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
    dp = Dispatcher()

    dp.include_router(router)
    dp.include_router(client_router)
    dp.include_router(admin_router)

    set_bot_instance(bot, MANAGER_CHAT_ID)

    return bot, dp


async def main():
    bot, dp = initiate_bot()

    logger.info("Bot Polling service started.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())