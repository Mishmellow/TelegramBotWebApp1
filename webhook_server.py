import time
import uuid
import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel, Field
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fastapi.staticfiles import StaticFiles  # Для обслуживания HTML/CSS/JS

from settings import MANAGER_CHAT_ID

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


BOT_INSTANCE: Optional[Bot] = None
PENDING_ORDERS: Dict[str, Any] = {}


def set_bot_instance(bot: Bot, manager_id: int):
    global BOT_INSTANCE
    BOT_INSTANCE = bot
    logger.info("Bot instance successfully set in api_service.")


class CartItem(BaseModel):
    name: str
    price: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class CartData(BaseModel):
    user_id: int = Field(..., description="Telegram ID пользователя")
    username: str = Field(None, description="Username пользователя")
    cart: list[CartItem]
    total: float = Field(..., gt=0)


api_router = APIRouter()


def create_order_keyboard(order_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"order_confirm_{order_id}"),
        InlineKeyboardButton(text="❌ Отменить", callback_data=f"order_cancel_{order_id}")
    )
    return builder.as_markup()


@api_router.post("/web-app/send-cart")
async def send_cart_data(data: CartData):

    if BOT_INSTANCE is None:
        logger.error("BOT_INSTANCE is not initialized. Cannot send message.")
        raise HTTPException(status_code=503, detail="Bot service not ready.")

    order_id = str(uuid.uuid4())[:8].upper()

    order_data = {
        'user_id': data.user_id,
        'cart': [item.model_dump() for item in data.cart],
        'total': data.total,
        'status': 'pending',
        'timestamp': time.time(),
        'username': data.username or 'N/A'
    }

    PENDING_ORDERS[order_id] = order_data
    logger.info(f"Order {order_id} saved to PENDING_ORDERS.")

    cart_details = "\n".join([f"- {item.name} ({item.quantity} шт.)" for item in data.cart])

    manager_message = (
        f"🚨 *НОВЫЙ ЗАКАЗ* | ID: `{order_id}`\n"
        f"👤 *Клиент:* [Пользователь](tg://user?id={data.user_id}) (ID: `{data.user_id}`)\n"
        f"@{data.username if data.username else 'Нет username'}\n"
        f"💰 *Сумма:* {data.total:.2f} ₴\n"
        f"--- Состав заказа ---\n"
        f"{cart_details}\n"
        f"------------------------\n"
        f"Нажмите кнопку для обработки:"
    )

    try:
        await BOT_INSTANCE.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=manager_message,
            reply_markup=create_order_keyboard(order_id),
            parse_mode='Markdown'
        )

        await BOT_INSTANCE.send_message(
            chat_id=data.user_id,
            text=f"✅ *Ваш заказ (ID: {order_id}) принят в обработку!* \nМенеджер скоро свяжется с вами.",
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Failed to send message to manager/client: {e}")
        raise HTTPException(status_code=500, detail="Failed to notify Telegram manager.")

    return {"message": "Order received and manager notified", "order_id": order_id}


app = FastAPI()

app.include_router(api_router)

app.mount(
    "/webapp",
    StaticFiles(directory="webapp_static_files", html=True),
    name="webapp_static"
)


@app.get('/')
async def health_check():
    return {"status": "ok", "message": "API service is running."}