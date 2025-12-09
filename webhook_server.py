import logging
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest

from settings import BOT_TOKEN, WEBHOOK_PATH, WEBHOOK_URL, WEBHOOK_SECRET, MANAGER_CHAT_ID, WEBHOOK_HOST
from api_service import set_bot_instance


from admin import admin_router
from api_service import APIRouter

from app.start import start_router
from app.menu_handlers import router as menu_router
from app.order_handlers import router as order_router

logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Web App & Bot Webhook Server")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

set_bot_instance(bot, MANAGER_CHAT_ID)

dp.include_router(start_router)
dp.include_router(menu_router)
dp.include_router(order_router)
dp.include_router(admin_router)

app.include_router(APIRouter)


@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):

    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        logger.warning("Получен запрос с неверным секретным токеном.")
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        update_json = await request.json()
    except Exception as e:
        logger.error(f"Не удалось распарсить JSON из Webhook: {e}")
        return Response(status_code=200)

    try:
        await dp.feed_raw_update(bot, update_json)
    except TelegramBadRequest as e:
        logger.error(f"Ошибка Telegram BadRequest при обработке Update: {e}")
    except Exception as e:
        logger.error(f"Критическая ошибка при обработке Update: {e}", exc_info=True)

    return Response(status_code=200)


STATIC_FILES_DIR = "webapp_static_files"
app.mount(
    "/webapp",
    StaticFiles(directory=STATIC_FILES_DIR, html=True),
    name="webapp_static"
)


@app.on_event("startup")
async def on_startup():
    if not BOT_TOKEN or not WEBHOOK_HOST:
        logger.error("🛑 Критические переменные BOT_TOKEN или WEBHOOK_HOST не установлены.")
        raise ValueError("BOT_TOKEN или WEBHOOK_HOST не установлены.")

    logger.info(f"Установка Webhook по URL: {WEBHOOK_URL}")

    try:
        webhook_success = await bot.set_webhook(
            url=WEBHOOK_URL,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True
        )
        if webhook_success:
            logger.info("✅ Webhook успешно установлен.")
        else:
            logger.error("🛑 Не удалось установить Webhook.")
    except Exception as e:
        logger.error(f"Ошибка при установке Webhook: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Удаление Webhook...")
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("Сессия бота закрыта. Сервер остановлен.")


@app.get("/")
async def root_status():
    webhook_info = await bot.get_webhook_info()
    return {
        "status": "running",
        "bot_id": bot.id,
        "webhook_url_set": webhook_info.url,
        "pending_updates": webhook_info.pending_update_count
    }