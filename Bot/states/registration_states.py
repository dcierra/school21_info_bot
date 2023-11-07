from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    enter_login = State()
    enter_password = State()
