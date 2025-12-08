import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup

from settings import BOT_TOKEN, MANAGER_CHAT_ID, WEBHOOK_HOST
from api_service import set_bot_instance

from admin import admin_router
from app.order_handlers import router as client_router
from app.keyboard import inline_category_keyboard, back_to_main_keyboard

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = Router()
WEB_APP_URL = f"{WEBHOOK_HOST}/webapp/index.html"


class UserForm(StatesGroup):
    waiting_for_web_app_data = State()


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



@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    keyboard = get_combined_start_keyboard()

    await message.answer(
        f"Привет, {message.from_user.full_name}! Добро пожаловать! Выберите раздел:",
        reply_markup=keyboard
    )


@router.callback_query(F.data == 'about_us')
async def handle_about_us(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        'ℹ️ Мы - команда Periphery, создающая лучшие решения...',
        reply_markup=back_to_main_keyboard()
    )


@router.callback_query(F.data == 'contacts')
async def handle_contacts(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        '📞 Свяжитесь с нами: Менеджер @ваш_менеджер...',
        reply_markup=back_to_main_keyboard()
    )


@router.callback_query(F.data == 'back_to_main')
async def back_to_main_menu(callback: CallbackQuery):
    await callback.answer('Возврат в главное меню.')
    main_menu_text = '👋 Вы вернулись в главное меню.'

    try:
        await callback.message.edit_text(
            main_menu_text,
            reply_markup=get_combined_start_keyboard()
        )
    except TelegramBadRequest:
        await callback.message.answer(
            main_menu_text,
            reply_markup=get_combined_start_keyboard()
        )


@router.message(F.text, StateFilter(None), ~Command('start'))
async def handle_text_message(message: Message):
    await message.reply('Извините, я не понял вас. Попробуйте /start, чтобы начать заново.',
                        reply_markup=get_combined_start_keyboard())


def initiate_bot() -> tuple[Bot, Dispatcher]:
    if not BOT_TOKEN:
        logger.error("🛑 ОШИБКА: Токен BOT_TOKEN не найден.")
        raise ValueError("BOT_TOKEN is not set.")

    bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
    dp = Dispatcher()

    dp.include_router(router)
    dp.include_router(client_router)
    dp.include_router(admin_router)

    set_bot_instance(bot, MANAGER_CHAT_ID)

    return bot, dp


async def main():
    try:
        bot, dp = initiate_bot()
        await bot.delete_webhook(drop_pending_updates=True)  # Очистка

        logger.info("🤖 Бот Polling запущен!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"🛑 Критическая ошибка: {e}")
    finally:
        if 'bot' in locals() and bot:
            await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("❌ Бот остановлен вручную.")