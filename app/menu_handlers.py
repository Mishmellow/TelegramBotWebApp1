from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter, Command

import logging

from app.keyboard import (
    inline_category_keyboard
)

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data == 'about_button')
async def handle_about_us(callback: CallbackQuery):
    await callback.answer()

    await callback.message.edit_text(
        'ℹ️ Мы - команда, создающая лучшие решения для Telegram.\nРаботает 24/7\n\n'
        '⬅️ Нажмите кнопку, чтобы вернуться в меню.',
        reply_markup=inline_category_keyboard()
    )


@router.callback_query(F.data == 'contacts_button')
async def handle_contacts(callback: CallbackQuery):
    await callback.answer()

    await callback.message.edit_text(
        '📞 Свяжитесь с нами через @ваш_менеджер или по почте ********.com\n\n'
        '⬅️ Нажмите кнопку, чтобы вернуться в меню.',
        reply_markup=inline_category_keyboard()
    )


@router.callback_query(F.data == 'back_to_main')
async def back_to_main_menu(callback: CallbackQuery):
    await callback.answer('Возврат в главное меню.')
    try:
        await callback.message.edit_text(
            '👋 Вы вернулись в главное меню.\n'
            'Теперь основной каталог доступен через кнопку "Открыть Магазин (Web App)".',
            reply_markup=inline_category_keyboard()
        )
    except TelegramBadRequest:
        await callback.message.answer(
            '👋 Вы вернулись в главное меню.\n'
            'Теперь основной каталог доступен через кнопку "Открыть Магазин (Web App)".',
            reply_markup=inline_category_keyboard()
        )


@router.message(F.text, StateFilter(None), ~Command('start'))
async def handle_text_message(message: Message):
    await message.reply('Извините, я не понял вас. Попробуйте /start, чтобы начать заново.')