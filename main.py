import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from settings import BOT_TOKEN, WEBHOOK_HOST, MANAGER_CHAT_ID
from api_service import set_bot_instance 
from admin import admin_router 


logging.basicConfig(level=logging.INFO)

async def main():
    if not BOT_TOKEN:
        print("🛑 ОШИБКА: Токен бота не установлен. Проверьте файл .env.")
        return
    
    if MANAGER_CHAT_ID == 0:
        print("🛑 ОШИБКА: ID менеджера не установлен или равен нулю. Проверьте переменную MANAGER_CHAT_ID в файле .env.")
        return

    bot = Bot(token=BOT_TOKEN, parse_mode='Markdown')
    dp = Dispatcher()

    set_bot_instance(bot, MANAGER_CHAT_ID)

    dp.include_router(admin_router) 

    @dp.message(CommandStart())
    async def command_start_handler(message: types.Message) -> None:
        
        web_app_url = f"{WEBHOOK_HOST}"

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🛍️ Перейти в Магазин",
                    web_app=types.WebAppInfo(url=web_app_url)
                )
            ]
        ])

        await message.answer(
            f"Привет, *{message.from_user.full_name}*! "
            "Добро пожаловать в наш онлайн-магазин! "
            "Нажмите кнопку ниже, чтобы начать покупки.",
            reply_markup=keyboard
        )

    try:
        print("🤖 Бот запущен и готов к работе...")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"🛑 Критическая ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("❌ Бот остановлен вручную.")