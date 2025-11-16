from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboard import inline_category_keyboard

router = Router()

@router.callback_query(F.data == 'about_button')
async def about_button(callback: CallbackQuery):
    await callback.message.answer('Мы - команда, создающая лучшие решения для Telegram.\nРаботает 24/7',
                                  reply_markup=inline_category_keyboard())

@router.callback_query(F.data == 'contacts_button')
async def contact_button(callback: CallbackQuery):
    await callback.message.answer('Свяжитесь с нами через @ваш_менеджер или по почте ********.com',
                                  reply_markup=inline_category_keyboard())