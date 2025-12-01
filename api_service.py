# Запускать: uvicorn api_service:app --reload
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from starlette.concurrency import run_in_threadpool


class Product(BaseModel):
    id: Optional[int] = None
    name: str
    type: str
    price: float
    description: Optional[str] = None


class WebAppCart(BaseModel):
    tg_user_id: int
    items: List[Product]


app = FastAPI(
    title="API Каталога Периферии",
    description='Простой REST API для получения информации о товарах.',
    version='1.0.0'
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    # New products(6 pieces)
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
]

last_id = max(p['id'] for p in PRODUCTS_DB) if PRODUCTS_DB else 200


def get_next_id():
    global last_id
    last_id += 1
    return last_id


def _get_all_products_sync():
    return PRODUCTS_DB


@app.get("/products", response_model=List[Product], summary='Получить весь каталог товаров')
async def get_all_products():
    return await run_in_threadpool(_get_all_products_sync)


@app.get('/products/{product_id}', response_model=Product, summary="Получить товар по ID")
async def get_product_by_id(product_id: int):
    product = await run_in_threadpool(
        lambda: next((p for p in PRODUCTS_DB if p['id'] == product_id), None)
    )

    if product is None:
        raise HTTPException(status_code=404, detail='Товар не найден')

    return product


@app.get('/products/type/{product_type}', response_model=List[Product],
         summary="Получить товары по типу (не используется фронтендом)")
async def get_products_by_type(product_type: str):
    filtered_products = await run_in_threadpool(
        lambda: [p for p in PRODUCTS_DB if p['type'].lower() == product_type.lower()]
    )

    return filtered_products


@app.post("/products", response_model=Product, status_code=201, summary='Добавить новый товар')
async def create_product(product: Product):
    new_id = get_next_id()
    new_product = product.model_dump()
    new_product['id'] = new_id
    PRODUCTS_DB.append(new_product)
    return new_product


@app.delete("/products/{product_id}", status_code=204, summary='Удалить товар по ID')
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