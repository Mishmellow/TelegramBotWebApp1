import uvicorn
import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from contextlib import asynccontextmanager

from settings import BOT_TOKEN, MANAGER_CHAT_ID, WEBHOOK_HOST
from database import init_db, populate_db

from app.start import router as start_router
from app.menu_handlers import router as menu_router
from app.order_handlers import router as order_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.error(f'DEBUG HOST VALUE: {WEBHOOK_HOST}')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(menu_router)
dp.include_router(order_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting up FastAPI service...')

    try:
        await init_db()
        await populate_db()

        if WEBHOOK_HOST.startswith('https://'):
            WEBHOOK_URL = f'{WEBHOOK_HOST}/webhook'
            await bot.set_webhook(url=WEBHOOK_URL)
            logger.info(f'Webhook started for {WEBHOOK_URL}')

            await bot.send_message(
                chat_id=MANAGER_CHAT_ID,
                text='✨ **WEBHOOK СЕРВИС ЗАПУЩЕН** ✨\nБот переключен на Webhooks.'
            )
        else:
            logger.warning(f'Running locally or in dev mode. Skipping Telegram Webhook setup.')

    except Exception as e:
        logger.error(f'FATAL ERROR during startup: {e}')

    yield

    logger.info('Shutting down FastAPI service...')
    await bot.delete_webhook()
    logger.info(f'Webhook deleted')

app = FastAPI(lifespan=lifespan)

@app.post('/webhook')
async def telegram_webhook(request: Request):
    update_json = await request.json()

    update = Update.model_validate(update_json)
    await dp.feed_update(bot, update)

    return {'ok': True}

@app.get('/')
async def health_check():
    return {'status": "ok", "message": "Bot server is running on Webhooks'}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)