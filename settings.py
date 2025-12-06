import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, '.env'))

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv('MANAGER_CHAT_ID', 0))
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
WEBAPP_URL = os.getenv('WEBAPP_URL')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set!!")
if not WEBAPP_URL:
    raise ValueError("WEBAPP_URL must be set!!")