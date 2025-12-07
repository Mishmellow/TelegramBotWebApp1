import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup

from app.keyboard import inline_category_keyboard
from app.menu_handlers import router as menu_router

from settings import BOT_TOKEN, MANAGER_CHAT_ID
from api_service import set_bot_instance
from admin import admin_router

logger = logging.getLogger(__name__)

router = Router()


class UserForm(StatesGroup):
    waiting_for_web_app_data = State()


@router.message(F.text == "/start")
async def command_start_handler(message: Message) -> None:

    await message.answer(
        "👋 Добро пожаловать! Нажмите кнопку ниже, чтобы открыть наше Web App, "
        "или выберите пункт меню.",
        reply_markup=inline_category_keyboard()
    )


def initiate_bot() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
    dp = Dispatcher()

    dp.include_router(router)
    dp.include_router(menu_router)
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