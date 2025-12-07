import uvicorn
import asyncio
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from settings import WEBHOOK_HOST, WEBHOOK_SECRET, BOT_TOKEN 
from api_service import router as api_router 
from bot import main as bot_main 

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Telegram Web App & Bot API Server",
    description="Сервер для Web App и API.",
    version="1.0.0"
)

bot_task = None 

app.include_router(api_router)

app.mount(
    "/webapp",
    StaticFiles(directory="docs", html=True), 
    name="webapp_static"
)

@app.on_event("startup")
async def startup_event():
    global bot_task
    if not BOT_TOKEN:
        logging.error("🛑 BOT_TOKEN не найден. Бот не будет запущен.")
        return
    
    try:
        bot_task = asyncio.create_task(bot_main()) 
        logging.info("🚀 Telegram Bot Polling started in background.")
    except Exception as e:
        logging.error(f"🛑 ОШИБКА: Не удалось запустить Polling бота: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global bot_task
    if bot_task and not bot_task.done():
        logging.info("👋 Завершение работы бота...")
        bot_task.cancel()
        try:
            await asyncio.wait_for(bot_task, timeout=5.0) 
        except asyncio.TimeoutError:
            logging.warning("⚠️ Задача бота не завершилась вовремя.")
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)