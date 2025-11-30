# Запускать: uvicorn api_service:app --reload
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional


class Product(BaseModel):
    id: Optional[int] = None
    name: str
    type: str
    price: float


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
    {"id": 201, "name": "Razer DeathAdder V3", "type": "Мышь", "price": 8990.0},
    {"id": 202, "name": "Logitech G Pro X", "type": "Клавиатура", "price": 14500.0},
    {"id": 203, "name": "HyperX Cloud Alpha", "type": "Гарнитура", "price": 7200.0},
    {"id": 204, "name": "SteelSeries Apex Pro", "type": "Клавиатура", "price": 19990.0},
]

last_id = max(p['id'] for p in PRODUCTS_DB) if PRODUCTS_DB else 200


def get_next_id():
    global last_id
    last_id += 1
    return last_id



@app.get("/products", response_model=List[Product], summary='Получить весь каталог товаров')
def get_all_products():
    return PRODUCTS_DB


@app.get('/products/{product_id}', response_model=Product, summary="Получить товар по ID")
def get_product_by_id(product_id: int):
    product = next((p for p in PRODUCTS_DB if p['id'] == product_id), None)

    if product is None:
        raise HTTPException(status_code=404, detail='Товар не найден')

    return product


@app.get('/products/type/{product_type}', response_model=List[Product],
         summary="Получить товары по типу (не используется фронтендом)")
def get_products_by_type(product_type: str):
    filtered_products = [
        p for p in PRODUCTS_DB if p['type'].lower() == product_type.lower()
    ]

    return filtered_products


@app.post("/products", response_model=Product, status_code=201, summary='Добавить новый товар')
def create_product(product: Product):
    new_id = get_next_id()
    new_product = product.model_dump()
    new_product['id'] = new_id
    PRODUCTS_DB.append(new_product)
    return new_product


@app.delete("/products/{product_id}", status_code=204, summary='Удалить товар по ID')
def delete_product(product_id: int):
    global PRODUCTS_DB

    index_to_delete = -1
    for i, p in enumerate(PRODUCTS_DB):
        if p['id'] == product_id:
            index_to_delete = i
            break

    if index_to_delete == -1:
        raise HTTPException(status_code=404, detail=f'Товар с ID {product_id} не найден')

    # Удаляем товар из списка
    PRODUCTS_DB.pop(index_to_delete)
    return  # Возвращаем 204 No Content