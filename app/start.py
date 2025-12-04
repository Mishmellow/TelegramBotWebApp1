from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Bot
import logging
import json

from app.keyboard import inline_category_keyboard
from api_service import PRODUCTS_DB, PENDING_ORDERS, create_manager_keyboard
from settings import MANAGER_CHAT_ID
import uuid
import time

router = Router()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    user_fullname = message.from_user.full_name
    logging.info(f"Пользователь {user_id}\n Присоединился {user_fullname}")

    await state.clear()

    await bot.send_message(
        text=f"👋 Привет, {message.from_user.full_name}!\n"
             "Я бот для приёма заказов.\n\n"
             "Выберите действие или используйте команду /help для справки.\n",
        chat_id=message.chat.id,
        reply_markup=inline_category_keyboard()
    )


@router.message(F.web_app_data)
async def handle_web_app_data(message: Message, bot: Bot):
    """Обрабатывает данные от Telegram Web App"""
    try:
        data = json.loads(message.web_app_data.data)
        user_id = data.get('tg_user_id', message.from_user.id)
        items = data.get('items', [])
        
        if not items:
            await message.answer("❌ Корзина пуста.")
            return
        
        order_id = str(uuid.uuid4()).split('-')[0].upper()
        
        order_details = []
        total_cost = 0
        
        for item in items:
            product_info = next((p for p in PRODUCTS_DB if p["id"] == item["id"]), None)
            if product_info:
                item_cost = product_info.get("price", 0.0) * item["quantity"]
                total_cost += item_cost
                order_details.append(f"   - {product_info['name']} (x{item['quantity']}): {item_cost:.2f} ₴")
        
        final_message_details = "\n".join(order_details)
        
        PENDING_ORDERS[order_id] = {
            'user_id': user_id,
            'details': final_message_details,
            'total': total_cost,
            'timestamp': int(time.time()),
            'status': 'pending'
        }
        
        user_link = f"[{message.from_user.full_name}](tg://user?id={user_id})"
        if message.from_user.username:
            user_link = f"[{message.from_user.full_name} (@{message.from_user.username})](tg://user?id={user_id})"
        
        manager_notification = (
            f"🔔 *НОВЫЙ ЗАКАЗ (ID: {order_id}) ИЗ WEB APP*\n"
            f"👤 {user_link}\n"
            f"--- Состав заказа ---\n"
            f"{final_message_details.strip()}\n"
            f"*💰 Общая сумма:* {total_cost:.2f} ₴"
        )
        
        user_confirmation = (
            f"✅ Ваш заказ (ID: {order_id}) принят!\n"
            f"Менеджер скоро свяжется с вами.\n"
            f"--- Детали заказа ---\n"
            f"{final_message_details.strip()}\n"
            f"💰 *Общая сумма:* {total_cost:.2f} ₴"
        )
        
        await bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=manager_notification,
            parse_mode='Markdown',
            reply_markup=create_manager_keyboard(order_id),
            disable_web_page_preview=True
        )
        
        await message.answer(user_confirmation, parse_mode='Markdown')
        
        logging.info(f"✅ Заказ {order_id} от пользователя {user_id} обработан через WebApp")
        
    except Exception as e:
        logging.error(f"Ошибка обработки web_app_data: {e}")
        await message.answer("❌ Произошла ошибка при обработке заказа.")