import uvicorn
import asyncio
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from settings import WEBHOOK_HOST, WEBHOOK_SECRET, BOT_TOKEN 
from api_service import router as api_router 
from bot import main as bot_main 
from api_service import set_bot_instance

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Telegram Web App & Bot API Server",
    description="Сервер для Web App и API.",
    version="1.0.0"
)

app.include_router(api_router)

app.mount(
    "/webapp",
    StaticFiles(directory="docs", html=True), 
    name="webapp_static"
)

@app.on_event("startup")
async def startup_event():
    if not BOT_TOKEN:
        logging.error("🛑 BOT_TOKEN не найден. Бот не будет запущен.")
        return

    try:
        asyncio.create_task(bot_main())
        logging.info("🚀 Telegram Bot Polling started in background.")
    except Exception as e:
        logging.error(f"🛑 ОШИБКА: Не удалось запустить Polling бота: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)