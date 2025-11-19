from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from app.menu_callbacks import PeripheryCallback

def get_main_reply_keyboard() -> ReplyKeyboardMarkup:

    keyboard = [
        [KeyboardButton(text='Сделать заказ')],
        [
            KeyboardButton(text='О нас'),
            KeyboardButton(text='Контакты')
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, selective=True)


def inline_category_keyboard():
    buy_button = InlineKeyboardButton(text='🛒Сделать заказ', callback_data='buy_button')
    about_button = InlineKeyboardButton(text='💡О нас', callback_data='about_button')
    contacts_button =InlineKeyboardButton(text='📞Контакты', callback_data='contacts_button')
    cart_button = InlineKeyboardButton(text='🧺Корзина', callback_data='view_cart')

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [buy_button, cart_button],
            [about_button, contacts_button],
        ],
    )
    return keyboard

PRODUCTS = {
    201: {'name': 'Razer DeathAdder V3', 'type': 'Мышь', 'price': 8990},
    202: {'name': 'Logitech G Pro X', 'type': 'Клавиатура', 'price': 14500 },
    203: {'name': 'HyperX Cloud Alpha', 'type': 'Гарнитура', 'price': 7200},
}

async def get_periphery_menu() -> InlineKeyboardMarkup:

    from database import get_all_products

    products = await get_all_products()
    buttons = []

    for product in products:
        callback_data = PeripheryCallback(
            action='add',
            item_id=product['id'],
            price=product['price'],
            name=product['name']
        ).pack()

        button = InlineKeyboardButton(
            text= f'🛒 {product["name"]} ({product["price"]} ₴)',
            callback_data=callback_data
        )
        buttons.append([button])

    checkout_button = InlineKeyboardButton(
        text='👉 Оформить заказ',
        callback_data='checkout'
    )
    buttons.append([checkout_button])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    cansel_button = InlineKeyboardButton(
        text='❌ Отмена заказа',
        callback_data='cansel_order'
    )
    return InlineKeyboardMarkup(inline_keyboard=[[cansel_button]])


def get_cart_keyboard(cart_items: list) -> InlineKeyboardMarkup:
    buttons = []

    for index, item in enumerate(cart_items):
        delete_callback = f'delete_item_{index}'

        button = InlineKeyboardButton(
            text= f'🗑️ Удалить {item["name"]}',
            callback_data=delete_callback
        )
        buttons.append([button])

    buttons.append([
        InlineKeyboardButton(text='👉 Оформить заказ', callback_data='checkout'),
    ])
    buttons.append([
        InlineKeyboardButton(text='🔙 Назад к каталогу', callback_data='show_categories'),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)