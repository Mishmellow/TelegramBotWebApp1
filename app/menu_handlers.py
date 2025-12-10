from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter, Command

import logging

from app.keyboard import (
    inline_category_keyboard,
    back_to_main_keyboard
)

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'about_button')
async def handle_about_us(callback: CallbackQuery):
    await callback.answer()

    back_keyboard = None

    await callback.message.edit_text(
        'ℹ️ Мы - команда Periphery, создающая лучшие решения для игрового оборудования и стриминга. '
        'Наши принципы: качество, надежность и отличная поддержка 24/7.\n\n'
        'Выберите, чтобы вернуться в главное меню.',
        reply_markup=back_keyboard
    )


@router.callback_query(F.data == 'contacts_button')
async def handle_contacts(callback: CallbackQuery):
    await callback.answer()

    back_keyboard = None

    await callback.message.edit_text(
        '📞 Свяжитесь с нами:\n'
        '• Менеджер: @ваш_менеджер\n'
        '• Почта: support@periphery.com\n'
        '• Адрес: Онлайн-склад в Киеве\n\n'
        'Выберите, чтобы вернуться в главное меню.',
        reply_markup=back_keyboard
    )


@router.callback_query(F.data == 'back_to_main')
async def back_to_main_menu(callback: CallbackQuery):
    await callback.answer('Возврат в главное меню.')

    main_menu_text = (
        '👋 Вы вернулись в главное меню.\n'
        'Чтобы открыть каталог товаров, нажмите кнопку "🛍️ Перейти в Магазин".'
    )

    try:
        await callback.message.edit_text(
            main_menu_text,
            reply_markup=inline_category_keyboard()
        )
    except TelegramBadRequest:
        await callback.message.answer(
            main_menu_text,
            reply_markup=inline_category_keyboard()
        )


@router.message(F.text, StateFilter(None), ~Command('start'))
async def handle_text_message(message: Message):
    await message.reply('Извините, я не понял вас. Попробуйте /start, чтобы начать заново.',
                        reply_markup=inline_category_keyboard())