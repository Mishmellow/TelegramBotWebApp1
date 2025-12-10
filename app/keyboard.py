from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters.callback_data import CallbackData
from typing import Optional
import logging
from settings import WEBAPP_URL

logger = logging.getLogger(__name__)

PRODUCTS = {
    201: {'name': 'Razer DeathAdder V3', 'type': 'Мышь', 'price': 8990},
    202: {'name': 'Logitech G Pro X', 'type': 'Клавиатура', 'price': 14500},
    203: {'name': 'HyperX Cloud Alpha', 'type': 'Гарнитура', 'price': 7200},
    204: {'name': 'SteelSeries Apex Pro', 'type': 'Клавиатура', 'price': 19990},
    205: {'name': 'Logitech G240', 'type': 'Коврик', 'price': 1899},
}


class PeripheryCallback(CallbackData, prefix='periph'):
    action: str
    item_id: Optional[int] = None


def inline_category_keyboard() -> InlineKeyboardMarkup:
    logger.info("DEBUG: Generating full inline category keyboard (3 rows).")

    web_app_button = InlineKeyboardButton(
        text="🛍️ Сделать Заказ",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )

    contacts_button = InlineKeyboardButton(text='📞 Контакты', callback_data='contacts')
    about_button = InlineKeyboardButton(text='ℹ️ О нас', callback_data='about_us')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [web_app_button],
        [contacts_button, about_button]
    ])
    return keyboard


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_periphery_menu() -> InlineKeyboardMarkup:
    keyboard = []

    items = list(PRODUCTS.items())
    for i in range(0, len(items), 2):
        row = []
        for j in range(2):
            if i + j < len(items):
                item_id, product = items[i + j]

                btn_text = f"[{product['type']}] {product['name']} ({product['price']} ₴)"
                callback_data = PeripheryCallback(action='add', item_id=item_id).pack()
                row.append(InlineKeyboardButton(text=btn_text, callback_data=callback_data))
        if row:
            keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(text='🛒 Корзина (0)', callback_data='view_cart'),
    ])
    keyboard.append([
        InlineKeyboardButton(text='⬅️ Главное меню', callback_data='back_to_main'),
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text='🚫 Отменить заказ', callback_data='cancel_order')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cart_keyboard(cart_items: list) -> InlineKeyboardMarkup:

    delete_buttons = []
    for index, item in enumerate(cart_items):
        delete_buttons.append(
            InlineKeyboardButton(
                text=f"❌ {item['name']}",
                callback_data=f'delete_item_{index}'
            )
        )

    delete_rows = [delete_buttons[i:i + 2] for i in range(0, len(delete_buttons), 2)]

    keyboard = delete_rows + [
        [InlineKeyboardButton(text='🛍️ Оформить заказ', callback_data='checkout')],
        [InlineKeyboardButton(text='⬅️ Продолжить покупки', callback_data='show_categories')],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)