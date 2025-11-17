import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найдет в переменных среды!")

MANAGER_CHAT_ID = int(os.getenv('MANAGER_CHAT_ID', 0))