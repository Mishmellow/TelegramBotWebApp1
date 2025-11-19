import os

from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv('MANAGER_CHAT_ID', 0))

WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')