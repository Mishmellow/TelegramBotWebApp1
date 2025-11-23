# Более значимые ипорты:
import logging

# Другие импорты
from aiogram.filters import CommandStart
from aiogram import Bot
from aiogram import Router
from aiogram.types import Message
from app.keyboard import inline_category_keyboard
from aiogram.fsm.context import FSMContext

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    user_fullname = message.from_user.full_name
    logging.info(f"Пользователь {user_id}\n Присоединился {user_fullname}")

    await state.clear()

    await bot.send_message(
        text=f"👋 Привет, {message.from_user.full_name}!\n"
             "Я бот для приёма заказов.\n\n"
             "Выберите категорию или используйте команду /help для справки.\n",
        chat_id=message.chat.id,
        reply_markup=inline_category_keyboard()
    )
