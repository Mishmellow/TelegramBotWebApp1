import asyncio
from aiogram import Dispatcher, Bot
import logging
from database import init_db, populate_db

from settings import MANAGER_CHAT_ID, BOT_TOKEN

from app.start import router as start_router
from app.menu_handlers import router as menu_router
from app.order_handlers import router as order_router


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
print('🟢 Запущено!')


async def main():
    await init_db()
    await populate_db()

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