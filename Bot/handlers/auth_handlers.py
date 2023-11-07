from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from Bot.states.registration_states import RegistrationState
from db_utils.commands import registration, get_user

router = Router()


@router.message(Command('registration'))
async def cmd_registration(message: Message, state: FSMContext):
    await state.clear()

    user = get_user.get_user(message.from_user.id)

    if not user:
        await message.answer('Введите <b>логин</b>: 📝', parse_mode='HTML')
        await state.set_state(RegistrationState.enter_login.state)
    else:
        await message.answer('Вы уже зарегистрированы ✅', parse_mode='HTML')


@router.message(RegistrationState.enter_login)
async def process_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)

    await message.answer('Введите <b>пароль</b>: 🔒', parse_mode='HTML')
    await state.set_state(RegistrationState.enter_password.state)


@router.message(RegistrationState.enter_password)
async def process_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    user_data = await state.get_data()

    await message.answer('<i>Пытаюсь подключиться к Школе 21..</i>', parse_mode='HTML')

    if await registration.registration(user_data, message):
        await message.answer('<b>Регистрация успешно завершена!</b> ✅', parse_mode='HTML')
    else:
        await message.answer(
            '<b>Не удалось подключиться к Школе 21 с введенными данными, попробуйте еще раз!</b> ❌',
            parse_mode='HTML'
        )

    await state.clear()

