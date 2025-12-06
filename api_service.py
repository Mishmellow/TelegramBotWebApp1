# web: uvicorn api_service:app --host 0.0.0.0 --port $PORT
# bot: python bot.py - it is for Procfile if process into bot, if will not work/ это код для прокфалй, на случай, если код не заработает

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any 
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from aiogram import Bot
from aiogram.types import Chat, InlineKeyboardMarkup, InlineKeyboardButton 
import uuid 
import time 

telegram_bot: Optional[Bot] = None 
MANAGER_CHAT_ID: Optional[int] = None

def set_bot_instance(bot_instance: Bot, manager_chat_id: int):
    global telegram_bot, MANAGER_CHAT_ID
    telegram_bot = bot_instance
    MANAGER_CHAT_ID = manager_chat_id


PENDING_ORDERS: Dict[str, Dict[str, Any]] = {} 


router = APIRouter(
    tags=["API Каталога"],
)


class Product(BaseModel):
    id: Optional[int] = None
    name: str
    type: str
    category: str
    price: float
    description: Optional[str] = None
    image_url: str

class CartItem(BaseModel):
    id: int
    quantity: int

class CartPayload(BaseModel):
    tg_user_id: int
    init_data: str
    items: List[CartItem]


PRODUCTS_DB = [
    {
        "id": 201,
        "name": "Razer DeathAdder V3",
        "type": "Мышь",
        "category": "Периферия",
        "price": 8990.0,
        "description": "Эргономичная игровая мышь с оптическим сенсором 30K DPI.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=DeathAdder"
    },
    {
        "id": 202,
        "name": "Logitech G Pro X",
        "type": "Клавиатура",
        "category": "Периферия",
        "price": 14500.0,
        "description": "Механическая клавиатура TKL с заменяемыми свитчами GX Blue.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=G+Pro+X+Keyboard"
    },
    {
        "id": 203,
        "name": "HyperX Cloud Alpha",
        "type": "Гарнитура",
        "category": "Аудио",
        "price": 7200.0,
        "description": "Игровая гарнитура с двойными камерами для чистого звука и микрофоном.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=Cloud+Alpha"
    },
    {
        "id": 204,
        "name": "SteelSeries Apex Pro",
        "type": "Клавиатура",
        "category": "Периферия",
        "price": 19990.0,
        "description": "Клавиатура с настраиваемыми механическими переключателями OmniPoint.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=Apex+Pro"
    },
    # АКСЕССУАРЫ / АУДИО (5-10)/ NEW PRODUCTS (5-10)
    {
        "id": 205,
        "name": "Logitech G502 Hero",
        "type": "Мышь",
        "category": "Периферия",
        "price": 3500.0,
        "description": "Классическая мышь с 11 программируемыми кнопками и регулировкой веса.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=G502+Hero"
    },
    {
        "id": 206,
        "name": "Samsung Odyssey G7",
        "type": "Монитор",
        "category": "Дисплеи",
        "price": 25500.0,
        "description": "Изогнутый игровой монитор 27 дюймов, 240 Гц, 1 мс.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=Odyssey+G7"
    },
    {
        "id": 207,
        "name": "Blue Yeti X",
        "type": "Микрофон",
        "category": "Аудио",
        "price": 11000.0,
        "description": "Профессиональный USB-микрофон с четырьмя режимами записи.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=Blue+Yeti+X"
    },
    {
        "id": 208,
        "name": "SteelSeries QcK Edge",
        "type": "Коврик",
        "category": "Аксессуары",
        "price": 950.0,
        "description": "Игровой коврик для мыши, края прошиты, XL размер.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=QcK+Edge"
    },
    {
        "id": 209,
        "name": "Elgato Stream Deck Mini",
        "type": "Контроллер",
        "category": "Стрим",
        "price": 5800.0,
        "description": "Мини-контроллер с 6 программируемыми LCD-клавишами для стриминга.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=Stream+Deck+Mini"
    },
    {
        "id": 210,
        "name": "Sony PlayStation 5 DualSense",
        "type": "Геймпад",
        "category": "Контроллеры",
        "price": 2990.0,
        "description": "Беспроводной геймпад с тактильной отдачей и адаптивными триггерами.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=DualSense"
    },
    # НОВЫЕ ТОВАРЫ (11-20)/ NEW PRODUCTS (11-20)
    {
        "id": 211,
        "name": "BenQ ZOWIE XL2546K",
        "type": "Монитор",
        "category": "Дисплеи",
        "price": 28000.0,
        "description": "Игровой монитор 24.5 дюйма, 240 Гц, DyAc+ технология.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=ZOWIE+XL2546K"
    },
    {
        "id": 212,
        "name": "Razer BlackShark V2 Pro",
        "type": "Гарнитура",
        "category": "Аудио",
        "price": 14990.0,
        "description": "Беспроводная киберспортивная гарнитура с технологией HyperSpeed.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=BlackShark+V2+Pro"
    },
    {
        "id": 213,
        "name": "Apple AirPods Pro 2",
        "type": "Наушники",
        "category": "Аудио",
        "price": 9500.0,
        "description": "Беспроводные наушники с активным шумоподавлением и Spatial Audio.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=AirPods+Pro+2"
    },
    {
        "id": 214,
        "name": "Logitech C920 HD Pro",
        "type": "Веб-камера",
        "category": "Стрим",
        "price": 3800.0,
        "description": "Веб-камера с разрешением 1080p, автофокусом и стереозвуком.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=Logi+C920"
    },
    {
        "id": 215,
        "name": "Glorious Model O Wireless",
        "type": "Мышь",
        "category": "Периферия",
        "price": 7990.0,
        "description": "Сверхлегкая беспроводная мышь с сотовой конструкцией.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=Model+O+Wireless"
    },
    {
        "id": 216,
        "name": "IKEA MARKUS (Кресло)",
        "type": "Мебель",
        "category": "Прочее",
        "price": 12500.0,
        "description": "Удобное рабочее/игровое кресло с высокой спинкой.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=MARKUS+Chair"
    },
    {
        "id": 217,
        "name": "HyperX Alloy Origins",
        "type": "Клавиатура",
        "category": "Периферия",
        "price": 9990.0,
        "description": "Компактная механическая клавиатура с переключателями HyperX Red.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=Alloy+Origins"
    },
    {
        "id": 218,
        "name": "Logitech G Astro A40",
        "type": "Гарнитура",
        "category": "Аудио",
        "price": 16990.0,
        "description": "Проводная гарнитура с MixAmp для профессионального звука.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=Astro+A40"
    },
    {
        "id": 219,
        "name": "Samsung T7 Portable SSD 1TB",
        "type": "Накопитель",
        "category": "Аксессуары",
        "price": 6500.0,
        "description": "Внешний SSD диск на 1 ТБ, скорость до 1050 МБ/с.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=T7+SSD"
    },
    {
        "id": 220,
        "name": "Logitech StreamCam",
        "type": "Веб-камера",
        "category": "Стрим",
        "price": 7990.0,
        "description": "Камера Full HD для вертикального и горизонтального стриминга.",
        "image_url": "https://placehold.co/400x200/4F46E5/FFFFFF?text=StreamCam"
    }
]

last_id = max(p['id'] for p in PRODUCTS_DB) if PRODUCTS_DB else 200


def get_next_id():
    global last_id
    last_id += 1
    return last_id


def _get_all_products_sync():
    return PRODUCTS_DB


@router.get("/products", response_model=List[Product], summary='Получить весь каталог товаров')
async def get_all_products():
    return await run_in_threadpool(_get_all_products_sync)


@router.get('/products/{product_id}', response_model=Product, summary="Получить товар по ID")
async def get_product_by_id(product_id: int):
    product = await run_in_threadpool(
        lambda: next((p for p in PRODUCTS_DB if p['id'] == product_id), None)
    )

    if product is None:
        raise HTTPException(status_code=404, detail='Товар не найден')

    return product


@router.get('/products/type/{product_type}', response_model=List[Product],
         summary="Получить товары по типу (не используется фронтендом)")
async def get_products_by_type(product_type: str):
    filtered_products = await run_in_threadpool(
        lambda: [p for p in PRODUCTS_DB if p['type'].lower() == product_type.lower()]
    )

    return filtered_products


@router.post("/products", response_model=Product, status_code=201, summary='Добавить новый товар')
async def create_product(product: Product):
    new_id = get_next_id()
    new_product = product.model_dump()
    new_product['id'] = new_id
    PRODUCTS_DB.append(new_product)
    return new_product


@router.delete("/products/{product_id}", status_code=204, summary='Удалить товар по ID')
async def delete_product(product_id: int):
    global PRODUCTS_DB

    def delete_sync():
        global PRODUCTS_DB
        index_to_delete = -1
        for i, p in enumerate(PRODUCTS_DB):
            if p['id'] == product_id:
                index_to_delete = i
                break

        if index_to_delete == -1:
            return False

        PRODUCTS_DB.pop(index_to_delete)
        return True

    deleted = await run_in_threadpool(delete_sync)

    if not deleted:
        raise HTTPException(status_code=404, detail=f'Товар с ID {product_id} не найден')

    return

def create_manager_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для менеджера для управления заказом."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить", 
                callback_data=f"order_confirm_{order_id}" 
            ),
            InlineKeyboardButton(
                text="❌ Отменить", 
                callback_data=f"order_cancel_{order_id}" 
            )
        ]
    ])


@router.post("/web-app/send-cart", summary="Обработка заказа от Telegram Web App")
async def send_cart_to_bot(payload: CartPayload):
    
    order_id = str(uuid.uuid4()).split('-')[0].upper() 
    
    print("-" * 50)
    print(f"✅ НОВЫЙ ЗАКАЗ (ID: {order_id}) ОТ TG ID: {payload.tg_user_id}")
    
    order_details = []
    total_cost = 0

    def calculate_cost_sync():
        nonlocal total_cost
        for item in payload.items:
            product_info = next((p for p in PRODUCTS_DB if p["id"] == item.id), None)

            if product_info:
                item_cost = product_info.get("price", 0.0) * item.quantity
                total_cost += item_cost
                detail = f"   - {product_info['name']} (x{item.quantity}): {item_cost:.2f} ₴"
                order_details.append(detail)
                print(detail)
            else:
                detail = f"   - Товар ID {item.id} не найден."
                order_details.append(detail)
                print(detail)

    await run_in_threadpool(calculate_cost_sync)
    
    final_message_details = "\n".join(order_details)
    print(f"💰 ОБЩАЯ СУММА ЗАКАЗА: {total_cost:.2f} ₴")
    print("-" * 50)
    
    if total_cost > 0:
        PENDING_ORDERS[order_id] = {
            'user_id': payload.tg_user_id,
            'details': final_message_details,
            'total': total_cost,
            'timestamp': int(time.time()),
            'status': 'pending'
        }
    
    if telegram_bot and MANAGER_CHAT_ID:
        
        
        user_link = f"[Пользователь (ID: {payload.tg_user_id})](tg://user?id={payload.tg_user_id})"
        
        try:
            chat: Chat = await telegram_bot.get_chat(payload.tg_user_id)
            
            display_name_parts = []
            if chat.first_name:
                display_name_parts.append(chat.first_name)
            if chat.last_name:
                display_name_parts.append(chat.last_name)
            
            name_part = " ".join(display_name_parts)
            
            if chat.username:
                username_part = f" (@{chat.username})"
            else:
                username_part = ""
            
            if name_part or chat.username:
                user_link = f"[{name_part}{username_part} (ID: {payload.tg_user_id})](tg://user?id={payload.tg_user_id})"

        except Exception as e:
            print(f"⚠️ НЕ УДАЛОСЬ ПОЛУЧИТЬ ИНФОРМАЦИЮ О ПОЛЬЗОВАТЕЛЕ (ID: {payload.tg_user_id}). Ошибка: {e}")
            
        user_info_display = f"👤 {user_link}"

        manager_notification = (
            f"🔔 *НОВЫЙ ЗАКАЗ (ID: {order_id}) ИЗ WEB APP*\n" 
            f"{user_info_display}\n" 
            f"--- Состав заказа ---\n"
            f"{final_message_details.strip()}\n"
            f"*💰 Общая сумма:* {total_cost:.2f} ₴"
        )
        
        user_confirmation = (
            f"✅ Ваш заказ (ID: {order_id}) принят в обработку!\n" 
            f"Спасибо за покупку. Менеджер скоро свяжется с вами.\n"
            f"--- Детали заказа ---\n"
            f"{final_message_details.strip()}\n"
            f"💰 *Общая сумма:* {total_cost:.2f} ₴"
        )
        
        try:
            await telegram_bot.send_message(
                chat_id=MANAGER_CHAT_ID,
                text=manager_notification,
                parse_mode='Markdown',
                reply_markup=create_manager_keyboard(order_id), 
                disable_web_page_preview=True 
            )
            
            await telegram_bot.send_message(
                chat_id=payload.tg_user_id,
                text=user_confirmation,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            print(f"🛑 ОШИБКА ОТПРАВКИ TELEGRAM: {e}")
    
    return {"status": "success", "message": f"Cart received, order ID {order_id} created."}