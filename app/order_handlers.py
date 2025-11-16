from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboard import get_periphery_menu, PRODUCTS, get_cancel_keyboard, get_cart_keyboard
from app.menu_callbacks import PeripheryCallback

from settings import MANAGER_CHAT_ID
from app.order_states import OrderStates

router = Router()

@router.callback_query(F.data == 'buy_button')
async def start_order(callback: CallbackQuery):
    await callback.answer()

    menu = await get_periphery_menu()

    await callback.message.edit_text(
        '🎮 Каталог игровой периферии:\nВыберите товар, чтобы добавить его в корзину.',
        reply_markup=menu
    )


@router.callback_query(F.data == 'show_categories')
async def return_to_catalog(callback: CallbackQuery):

    menu = await get_periphery_menu()

    await callback.message.edit_text(
        '🎮 Каталог периферии:',
        reply_markup=menu
    )
    await callback.answer()


@router.callback_query(F.data == 'checkout')
async def start_checkout(callback: CallbackQuery, state: FSMContext):

    await callback.answer()

    data = await state.get_data()
    cart = data.get('cart', [])

    if not cart:
        return await callback.answer('❌ Ваша корзина пуста! Добавьте товар.', show_alert=True)

    await state.set_state(OrderStates.waiting_for_name)

    await callback.message.edit_text(
        '✅ Отлично! В корзине '
        f'{len(cart)} товаров.\n\n'
        'Для оформления заказа введите, пожалуйста, ваше имя:',
        reply_markup=get_cancel_keyboard()
    )


@router.callback_query(PeripheryCallback.filter(F.action == 'add'))
async def handle_add_product(
        callback: CallbackQuery,
        callback_data: PeripheryCallback,
        state: FSMContext,
):

    product_info = PRODUCTS.get(callback_data.item_id)

    if not product_info:
        await callback.answer('Ошибка: Товар не найден в каталоге.', show_alert=True)
        return

    product_name = product_info['name']
    product_price = product_info['price']

    data = await state.get_data()
    cart = data.get('cart', [])

    item_to_add = {
        'id': callback_data.item_id,
        'name': product_name,
        'price': product_price,
    }
    cart.append(item_to_add)

    await state.update_data(cart=cart)
    await callback.answer(f'✅ Добавлено: {product_name}. В корзине {len(cart)} товаров.', show_alert=False)

    update_menu = await get_periphery_menu()

    await callback.message.edit_text(
        f'{product_name} добавлен.\nВ корзине: {len(cart)} товаров. Выберите еще или оформите заказ.',
        reply_markup=update_menu
    )


@router.message(OrderStates.waiting_for_name)
async def proces_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await state.set_state(OrderStates.waiting_for_address)

    await message.answer(
        f'Приятно познакомиться, {name}!\n'
        f"Теперь введите, пожалуйста, точный адрес доставки (улица, дом, квартира):",
        reply_markup=get_cancel_keyboard()
    )


@router.message(OrderStates.waiting_for_address)
async def address_process(message: Message, state: FSMContext, bot: Bot):

    await state.update_data(address=message.text)
    data = await state.get_data()

    user_name = data.get('name')
    user_address = data.get('address')
    cart = data.get('cart', [])

    order_details = "\n".join([f"- {item['name']} ({item['price']} ₴)" for item in cart])
    total_price = sum(item['price'] for item in cart)

    manager_message = (
        "🔔 **НОВЫЙ ЗАКАЗ!** 🚀\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
        f"👤 Клиент: **{user_name}**\n"
        f"🏠 Адрес доставки: **{user_address}**\n\n"

        f"🛒 **СОСТАВ ЗАКАЗА ({len(cart)} позиций):**\n"
        f"{order_details}\n\n"

        f"💳 **ИТОГО К ОПЛАТЕ:** **{total_price} ₴**\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "✨ Ожидается подтверждение оплаты."
    )

    try:
        await bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=manager_message,
            parse_mode='Markdown'
        )
    except TelegramBadRequest as e:
        print(f'Ошибка Markdown при отправке менеджеру: {e}. Отправка как обычный текст.')

        plain_text_message = manager_message.replace('**', '').replace('—', '-')

        await bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=plain_text_message,
        )
    except Exception as e:
        print(f'Критическая ошибка при отправке менеджеру: {e}')

    summary = (
        f"✅ Заказ оформлен!\n\n"
        f"Имя: {user_name}\n"
        f"Адрес доставки: {user_address}\n\n"
        "Спасибо за заказ! Нажмите /start, чтобы начать новый."
    )

    await message.answer(summary)
    await state.clear()

@router.callback_query(F.data == 'view_cart')
async def view_cart(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    cart = data.get('cart', [])

    if not cart:
        await callback.answer('❌ Ваша корзина пуста!', show_alert=True)
        return

    await callback.answer()

    order_details = "\n".join([f"— {item['name']} ({item['price']} ₴)" for item in cart])
    total_price = sum(item['price'] for item in cart)

    cart_summary = (
        "🛒СОДЕРЖИМОЕ ВАШЕЙ КОРЗИНЫ:\n\n"
        f"{order_details}\n\n"
        f"💰 ИТОГО: {total_price} ₴"
    )

    await callback.message.edit_text(
        cart_summary,
        reply_markup=get_cart_keyboard(cart_items=cart),
        parse_mode='MarkdownV2'
    )


@router.callback_query(F.data.startswith('delete_item_'))
async def delete_item_from_cart(callback: CallbackQuery, state: FSMContext):

    try:
        item_index = int(callback.data.split('_')[-1])
    except ValueError:
        await callback.answer('Ошибка данных', show_alert=True)
        return

    data = await state.get_data()
    cart = data.get('cart', [])

    if 0 <= item_index < len(cart):
        deleted_item = cart.pop(item_index)
        await state.update(cart=cart)

        await callback.answer(f'🗑️ Товар {deleted_item['name']} удален из корзины.', show_alert=False)

        if not cart:
            await callback.message.edit_text(
                '🛒 Ваша корзина теперь пуста.',
                reply_markup=await get_periphery_menu()
            )
            return

        order_details = "\n".join([f"— {item['name']} ({item['price']} ₴)" for item in cart])
        total_price = sum(item['price'] for item in cart)

        cart_summary = (
            "🛒 **СОДЕРЖИМОЕ ВАШЕЙ КОРЗИНЫ (Обновлено):**\n\n"
            f"{order_details}\n\n"
            f"💰 **ИТОГО:** {total_price} ₴"
        )

        await callback.message.edit_text(
            cart_summary,
            reply_markup=get_cart_keyboard(cart_items=cart),
            parse_mode='Markdown'
        )

    else:
        await callback.answer('Ошибка: Товар уже удален или не существует.', show_alert=True)


@router.callback_query(F.data == 'cancel_order', OrderStates.waiting_for_name)
@router.callback_query(F.data == 'cancel_order', OrderStates.waiting_for_address)
async def cancel_order(callback: CallbackQuery, state: FSMContext):

    await state.clear()
    await callback.message.delete()

    menu = await get_periphery_menu()
    await callback.message.answer(
        '🚫 Оформление заказа отменено.',
        reply_markup=menu
    )
    await callback.answer()