# Более значимые ипорты:
import logging

# Другие импорты
from aiogram.filters import CommandStart, Command
from aiogram import Router
from aiogram.types import Message
from app.keyboard import inline_category_keyboard


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    user_fullname = message.from_user.full_name
    logging.info(f"Пользователь {user_id}\n Присоединился {user_fullname}")

    await message.reply(f'Привет {user_fullname}\nТвой id: {user_id}\nЧем могу помочь?',
                        reply_markup=inline_category_keyboard())


@router.message(Command('help'))
async def help_message(message: Message):
    await message.reply('How i can help you?')