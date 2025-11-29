from aiogram.fsm.state import State, StatesGroup

class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_address = State()
    waiting_for_phone = State()
    waiting_for_information = State()
    confirm_order = State()
    waiting_for_receipt = State()
