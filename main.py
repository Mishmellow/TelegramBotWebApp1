# from aiogram import Dispatcher, Bot
# import logging
# from database import init_db, populate_db
#
# from settings import MANAGER_CHAT_ID, BOT_TOKEN
#
# from app.start import router as start_router
# from app.menu_handlers import router as menu_router
# from app.order_handlers import router as order_router
#
#
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#
# async def on_startup(bot: Bot):
#     await bot.send_message(
#         chat_id=MANAGER_CHAT_ID,
#         text="✨СЕРВИС ЗАПУЩЕН ✨\nБот вышел в онлайн и готов к работе."
#     )
#
# async def main():
#     await init_db()
#     await populate_db()
#
#     bot = Bot(token=BOT_TOKEN)
#
#     dp = Dispatcher()
#
#     dp.startup.register(on_startup)
#     dp.include_router(order_router)
#     dp.include_router(menu_router)
#     dp.include_router(start_router)
#
#
# if __name__ == '__main__':
#     pass