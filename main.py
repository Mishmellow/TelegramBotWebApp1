import asyncio
from aiogram import Dispatcher, Bot
import logging
import os
from dotenv import load_dotenv
from database import init_db, populate_db

from app.start import router as start_router
from app.menu_handlers import router as menu_router
from app.order_handlers import router as order_router

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
print('🟢 Запущено!')

BOT_TOKEN = os.getenv('BOT_TOKEN')
MANAGER_CHAT_ID = os.getenv('MANAGER_CHAT_ID')

async def main():
    await init_db()
    await populate_db()

    if not BOT_TOKEN:
        print('🛑 Ошибка: BOT_TOKEN не найден в переменных окружения (.env)')
        return

    bot = Bot(token=BOT_TOKEN)

    dp = Dispatcher()

    dp.include_router(order_router)
    dp.include_router(menu_router)
    dp.include_router(start_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
    except Exception as e:
        logging.error(f'Произошла фатальная ошибка: {e}')