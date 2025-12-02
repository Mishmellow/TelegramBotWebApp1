from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

import logging

from app.keyboard import get_periphery_menu, PRODUCTS, get_cancel_keyboard, get_cart_keyboard, PeripheryCallback
from app.order_states import OrderStates
from app.keyboard import inline_category_keyboard

from settings import MANAGER_CHAT_ID

logger = logging.getLogger(__name__)

router = Router()

PAYMENT_DETAILS_TEXT = (
    "💳 Номер карты: 4444 5555 6666 7777(это тестовая карта\n)"
    " \nБот создан в образовательных целях!\n"
    "👤 Получатель: В. М. Фесик\n\n"
    "💰 ВНИМАНИЕ! Сумма к оплате будет указана выше.\n"
    "Срок на оплату: 2 часа."
)


@router.callback_query(F.data == 'buy_button')
async def start_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    cart_count = len(data.get('cart', []))

    menu = await get_periphery_menu()

    for row in menu.inline_keyboard:
        for button in row:
            if button.callback_data == 'view_cart':
                button.text = f'🛒 Корзина ({cart_count})'

    await callback.message.edit_text(
        '🎮 Каталог игровой периферии:\nВыберите товар, чтобы добавить его в корзину.',
        reply_markup=menu
    )


@router.callback_query(F.data == 'back_to_main')
async def back_to_main_menu(callback: CallbackQuery):
    await callback.answer('Возврат в главное меню.')
    await callback.message.edit_text(
        '👋 Вы вернулись в главное меню.\n'
        'Выберите действие или используйте команду /help для справки.',
        reply_markup=inline_category_keyboard()
    )


@router.callback_query(F.data == 'show_categories')
async def return_to_catalog(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    cart_count = len(data.get('cart', []))

    menu = await get_periphery_menu()

    for row in menu.inline_keyboard:
        for button in row:
            if button.callback_data == 'view_cart':
                button.text = f'🛒 Корзина ({cart_count})'

    await callback.message.edit_text(
        '🎮 Каталог периферии:',
        reply_markup=menu
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

    for row in update_menu.inline_keyboard:
        for button in row:
            if button.callback_data == 'view_cart':
                button.text = f'🛒 Корзина ({len(cart)})'

    await callback.message.edit_text(
        f'{product_name} добавлен.\nВ корзине: {len(cart)} товаров. Выберите еще или оформите заказ.',
        reply_markup=update_menu
    )


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
        "🛒 СОДЕРЖИМОЕ ВАШЕЙ КОРЗИНЫ:\n\n"
        f"{order_details}\n\n"
        f"💰 ИТОГО: {total_price} ₴"
    )

    await callback.message.edit_text(
        cart_summary,
        reply_markup=get_cart_keyboard(cart_items=cart),
        parse_mode='Markdown'
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
        await state.update_data(cart=cart)

        await callback.answer(f'🗑️ Товар {deleted_item["name"]} удален из корзины.', show_alert=False)

        if not cart:
            menu = await get_periphery_menu()
            for row in menu.inline_keyboard:
                for button in row:
                    if button.callback_data == 'view_cart':
                        button.text = f'🛒 Корзина (0)'

            await callback.message.edit_text(
                '🛒 Ваша корзина теперь пуста.',
                reply_markup=menu
            )
            return

        order_details = "\n".join([f"— {item['name']} ({item['price']} ₴)" for item in cart])
        total_price = sum(item['price'] for item in cart)

        cart_summary = (
            "🛒 СОДЕРЖИМОЕ ВАШЕЙ КОРЗИНЫ (Обновлено):\n\n"
            f"{order_details}\n\n"
            f"💰 ИТОГО: {total_price} ₴"
        )

        await callback.message.edit_text(
            cart_summary,
            reply_markup=get_cart_keyboard(cart_items=cart),
            parse_mode='Markdown'
        )

    else:
        await callback.answer('Ошибка: Товар уже удален или не существует.', show_alert=True)


@router.callback_query(F.data == 'checkout')
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    cart = data.get('cart', [])

    if not cart:
        menu = await get_periphery_menu()
        for row in menu.inline_keyboard:
            for button in row:
                if button.callback_data == 'view_cart':
                    button.text = f'🛒 Корзина (0)'

        return await callback.message.edit_text(
            '❌ Ваша корзина пуста! Добавьте товар, чтобы оформить заказ.',
            reply_markup=menu
        )

    await state.set_state(OrderStates.waiting_for_name)

    await callback.message.edit_text(
        '✅ Отлично! В корзине '
        f'{len(cart)} товаров.\n\n'
        'Для оформления заказа введите, пожалуйста, ваше имя:',
        reply_markup=get_cancel_keyboard()
    )


@router.message(OrderStates.waiting_for_name, F.text, ~F.text.startswith('/'))
async def proces_name(message: Message, state: FSMContext):
    current_state = await state.get_state()
    logger.info(
        f"proces_name called for user {message.from_user.id}. Current state: {current_state}. Text: '{message.text}'")

    name = message.text
    await state.update_data(name=name)
    await state.set_state(OrderStates.waiting_for_address)

    await message.answer(
        f'Приятно познакомиться, {name}!\n'
        f"Теперь введите, пожалуйста, точный адрес доставки (улица, дом, квартира):",
        reply_markup=get_cancel_keyboard()
    )


@router.message(OrderStates.waiting_for_address, F.text, ~F.text.startswith('/'))
async def address_process(message: Message, state: FSMContext, bot: Bot):
    current_state = await state.get_state()
    logger.info(
        f"address_process called for user {message.from_user.id}. Current state: {current_state}. Text: '{message.text}'")

    await state.update_data(address=message.text)
    data = await state.get_data()

    user_name = data.get('name')
    user_address = data.get('address')
    cart = data.get('cart', [])

    order_details = "\n".join([f"- {item['name']} ({item['price']} ₴)" for item in cart])
    total_price = sum(item['price'] for item in cart)

    manager_message = (
        "<b>🔔 НОВЫЙ ЗАКАЗ!</b> 🚀\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
        f"👤 Клиент: {user_name} (ID: <code>{message.from_user.id}</code>)\n"
        f"🏠 Адрес доставки: {user_address}\n\n"

        f"🛒 СОСТАВ ЗАКАЗА ({len(cart)} позиций):\n"
        f"{order_details}\n\n"

        f"<b>💳 ИТОГО К ОПЛАТЕ: {total_price} ₴</b>\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "✨ Ожидается подтверждение оплаты (квитанция)."
    )

    try:
        await bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=manager_message,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f'Критическая ошибка при отправке менеджеру: {e}')
        await bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=f"Критическая ошибка при отправке заказа от пользователя {message.from_user.id}: {e}"
        )

    await state.set_state(OrderStates.waiting_for_receipt)

    payment_instruction = (
        f"<b>🔔 Ваш заказ принят в обработку!</b>\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
        f"<b>💳 К ОПЛАТЕ: {total_price} ₴</b>\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
        f"ИНСТРУКЦИИ ДЛЯ ОПЛАТЫ:\n"
        f"{PAYMENT_DETAILS_TEXT}\n\n"
        "➡️ ОБЯЗАТЕЛЬНО пришлите фото или скриншот квитанции в этот чат, чтобы менеджер мог активировать ваш заказ.\n"
        "🚫 Для отмены заказа введите /start."
    )

    await message.answer(payment_instruction, parse_mode='HTML')


@router.message(OrderStates.waiting_for_receipt, F.photo)
async def process_receipt_photo(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_name = data.get('name', 'Неизвестный')
    total_price = sum(item['price'] for item in data.get('cart', []))
    client_id = message.from_user.id

    username = message.from_user.username if message.from_user.username else 'Нет юзернейма'

    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Активировать", callback_data=f'approve_{client_id}'),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f'reject_{client_id}')
        ]
    ])

    caption = (
        f"<b>🔔 ПОЛУЧЕНА КВИТАНЦИЯ</b>\n"
        f"➖➖➖➖➖➖➖➖➖➖➖➖\n"
        f"👤 Клиент: <a href='tg://user?id={client_id}'>{user_name}</a> (@{username})\n"
        f"💳 Сумма заказа: <b>{total_price} ₴</b>\n"
        f"ID Чата: <code>{client_id}</code>\n\n"
        f"Проверьте квитанцию и примите решение:"
    )

    try:
        await bot.send_photo(
            chat_id=MANAGER_CHAT_ID,
            photo=message.photo[-1].file_id,
            caption=caption,
            reply_markup=admin_keyboard,
            parse_mode='HTML'
        )

        await message.answer(
            "📄 <b>Квитанция получена!</b>\n"
            "Менеджер проверяет ваш платеж. Мы сообщим вам о результате.",
            parse_mode='HTML'
        )
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка при пересылке квитанции администратору: {e}")
        await message.answer(
            "❌ Произошла ошибка при отправке вашей квитанции. Попробуйте еще раз или свяжитесь с поддержкой.")


@router.message(OrderStates.waiting_for_receipt, F.text,
                ~F.text.startswith('/'))
async def process_receipt_text_error(message: Message):
    await message.answer("Пожалуйста, прикрепите <b>фотографию</b> или <b>скриншот</b> квитанции об оплате.", parse_mode='HTML')


@router.callback_query(F.data.startswith('approve_'))
async def admin_approve_order(callback: CallbackQuery, bot: Bot):
    await callback.answer("Заказ активирован.")

    try:
        client_id = int(callback.data.split('_')[-1])

        admin_username = callback.from_user.username if callback.from_user.username else 'Админ'

        await bot.send_message(
            chat_id=client_id,
            text="✅ <b>Ваш заказ успешно активирован!</b>\n"
                 "Спасибо за покупку. Менеджер свяжется с вами для уточнения деталей доставки.",
            parse_mode='HTML'
        )

        await callback.message.edit_caption(
            caption=f"{callback.message.caption}\n\n"
                    f"🟢 <b>АКТИВИРОВАНО</b> менеджером: @{admin_username}",
            reply_markup=None,
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Ошибка активации заказа для клиента {client_id}: {e}")
        await bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=f"❌ Ошибка активации заказа ID {client_id}: {e}"
        )


@router.callback_query(F.data.startswith('reject_'))
async def admin_reject_order(callback: CallbackQuery, bot: Bot):
    await callback.answer("Заказ отклонен.")

    try:
        client_id = int(callback.data.split('_')[-1])
        admin_username = callback.from_user.username if callback.from_user.username else 'Админ'

        await bot.send_message(
            chat_id=client_id,
            text="❌ <b>Ошибка оплаты.</b>\n"
                 "Ваша квитанция не подтверждена. Пожалуйста, убедитесь, что вы оплатили полную сумму и прислали правильный скриншот. Начните заново командой /start.",
            parse_mode='HTML'
        )

        await callback.message.edit_caption(
            caption=f"{callback.message.caption}\n\n"
                    f"🔴 <b>ОТКЛОНЕНО</b> менеджером: @{admin_username}",
            reply_markup=None,
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Ошибка отклонения заказа для клиента {client_id}: {e}")
        await bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=f"❌ Ошибка отклонения заказа ID {client_id}: {e}"
        )


@router.callback_query(F.data == 'cancel_order', OrderStates.waiting_for_name)
@router.callback_query(F.data == 'cancel_order', OrderStates.waiting_for_address)
@router.callback_query(F.data == 'cancel_order', OrderStates.waiting_for_receipt)
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    logger.info(f"User {callback.from_user.id} cancelled order from state {await state.get_state()}")

    await state.clear()

    menu = inline_category_keyboard()

    try:
        await callback.message.edit_text(
            '🚫 Оформление заказа отменено. Вы вернулись в главное меню.',
            reply_markup=menu
        )
        await callback.answer('Заказ отменен. Возврат в меню.')
    except TelegramBadRequest:
        await callback.message.answer(
            '🚫 Оформление заказа отменено. Вы вернулись в главное меню.',
            reply_markup=menu
        )
        await callback.answer('Заказ отменен. Возврат в меню.')