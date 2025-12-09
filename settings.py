from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

manager_id_str = os.getenv("MANAGER_CHAT_ID")
if manager_id_str:
    try:
        MANAGER_CHAT_ID = int(manager_id_str)
    except ValueError:
        raise ValueError("MANAGER_CHAT_ID в .env должен быть числом!")
else:
    MANAGER_CHAT_ID = None

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
WEBHOOK_PATH = "/webhook"

WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else None

WEBAPP_URL = os.getenv("WEBAPP_URL", f"{WEBHOOK_HOST}/webapp/index.html" if WEBHOOK_HOST else None)


if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN должен быть установлен в .env!")

if not WEBHOOK_HOST:
    print("⚠️ ПРЕДУПРЕЖДЕНИЕ: WEBHOOK_HOST не установлен. Webhook не будет работать.")