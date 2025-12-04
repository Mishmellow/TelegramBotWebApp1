from aiogram import Router, types, F, Bot
from aiogram.types import CallbackQuery
from api_service import PENDING_ORDERS, MANAGER_CHAT_ID 
from typing import Literal

admin_router = Router()


@admin_router.message(F.text == "/admin")
async def handle_admin_check(message: types.Message):
    if message.chat.id == MANAGER_CHAT_ID:
        await message.answer(
            "✅ Вы успешно авторизованы как МЕНЕДЖЕР. Ожидайте новых заказов!"
        )
    else:
        await message.answer(
            "🛑 Доступ запрещен. Вы не являетесь менеджером."
        )


async def process_order_action(
    callback: CallbackQuery, 
    action: Literal['confirm', 'cancel'],
    bot: Bot
):
    try:
        order_id = callback.data.split('_')[-1]
    except IndexError:
        await callback.answer("Ошибка данных колбэка.")
        return

    if order_id not in PENDING_ORDERS:
        await callback.answer(
            f"Заказ ID {order_id} уже обработан или не существует.", 
            show_alert=True
        )

        try:
            await callback.message.edit_text(
                f"{callback.message.text}\n\n*🛑 Заказ был обработан ранее.*",
                parse_mode='Markdown'
            )
        except Exception:
            pass 
        return

    order_data = PENDING_ORDERS.pop(order_id)
    user_id = order_data['user_id']
    total_cost = order_data['total']
    
    if action == 'confirm':
        status_text = "✅ ПОДТВЕРЖДЕН"
        manager_message_suffix = "\n\n✅ *Заказ подтвержден.* Свяжитесь с клиентом для уточнения деталей."
        user_notification_text = (
            f"🎉 *Ваш заказ ID {order_id} ПОДТВЕРЖДЕН!* 🎉\n"
            f"Менеджер свяжется с вами в ближайшее время для организации доставки.\n"
            f"💰 Общая сумма: {total_cost:.2f} ₴"
        )
    else:
        status_text = "❌ ОТМЕНЕН"
        manager_message_suffix = "\n\n❌ *Заказ отменен.*"
        user_notification_text = (
            f"😔 *Ваш заказ ID {order_id} ОТМЕНЕН.* 😔\n"
            f"Причина: (Менеджер может написать причину, ответив на это сообщение.)\n"
            f"Вы можете оформить новый заказ, если это была ошибка."
        )

    try:
        await bot.send_message(
            chat_id=user_id,
            text=user_notification_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"🛑 ОШИБКА: Не удалось отправить уведомление пользователю {user_id}. {e}")

    try:
        new_manager_text = callback.message.text.split("--- Состав заказа ---")[0] + manager_message_suffix
        
        await callback.message.edit_text(
            new_manager_text,
            parse_mode='Markdown',
            reply_markup=None 
        )
    except Exception as e:
        print(f"🛑 ОШИБКА редактирования сообщения менеджеру: {e}")
        
    await callback.answer(f"Заказ ID {order_id} {status_text}!", show_alert=False)


@admin_router.callback_query(F.data.startswith('order_confirm_'))
async def handle_confirm_callback(callback: CallbackQuery, bot: Bot):
    """Обрабатывает нажатие кнопки 'Подтвердить'."""
    await process_order_action(callback, 'confirm', bot)

@admin_router.callback_query(F.data.startswith('order_cancel_'))
async def handle_cancel_callback(callback: CallbackQuery, bot: Bot):
    """Обрабатывает нажатие кнопки 'Отменить'."""
    await process_order_action(callback, 'cancel', bot)