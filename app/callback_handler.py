# from aiogram import Router, F
# from aiogram.types import CallbackQuery
#
# router = Router()
#
# @router.message(F.data == 'about_button')
# async def about_button(callback: CallbackQuery):
#     text = 'Мы — команда, создающая лучшие решения для Telegram.'
#     await callback.message.edit_text(text, reply_markup=None)
#     await callback.answer()
#
# @router.message(F.data == 'contacts_button')
# async def contacts_button(callback: CallbackQuery):
#     text = 'Свяжитесь с нами через @ваш_менеджер.'
#     await callback.message.edit_text(text, reply_markup=None)
#     await callback.answer()
