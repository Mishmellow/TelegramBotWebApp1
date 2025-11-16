from aiogram.filters.callback_data import CallbackData

class PeripheryCallback(CallbackData, prefix='per'):
    action: str
    item_id: int
    price: int
    name: str