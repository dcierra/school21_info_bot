import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from db_utils.commands.get_user import get_user
from db_utils.commands.set_token import set_token
from SchoolParser.SchoolRequests import Request

router = Router()


def create_request(user):
    req = Request(
        cookies={'tokenId': user.token_id},
        headers={'schoolid': user.school_id}
    )

    if req.test_request() == 200:
        return req
    else:
        set_token(user)
        return create_request(user)


@router.message(Command('get_events'))
async def cmd_get_events(message: Message):
    user = get_user(message.from_user.id)

    if user:
        req = create_request(user)
        events = req.get_events(print_result=False)

        events_text = "<b>События:</b>\n\n"
        for event_id, event_info in events.items():
            events_text += f"📅 <b>{event_id}</b>\n"
            events_text += f"👤 <i>Имя:</i> {event_info['Имя']}\n"
            events_text += f"📝 <i>Описание:</i> {event_info['Описание']}\n"
            events_text += f"⏰ <i>Начало через:</i> {event_info['Начало через']}\n\n"

        await message.answer(events_text, parse_mode='HTML')
    else:
        await message.answer('<b>Вам необходимо зарегистрироваться '
                             'для выполнения этой команды!</b> ❌', parse_mode='HTML')


@router.message(Command('get_campus_occupied'))
async def cmd_get_campus_occupied(message: Message):
    user = get_user(message.from_user.id)

    if user:
        req = create_request(user)
        campus_map = req.get_campus_plan_occupied(print_result=False)

        campus_text = "🏢 <b>Занятость кампусов:</b>\n\n"
        for campus_id, campus_info in campus_map.items():
            campus_text += f"<b>{campus_id}</b>\n"
            campus_text += f"🔒 <i>Занято мест:</i> <b>{campus_info['Занято мест']}</b>\n"
            campus_text += f"🔓 <i>Всего мест:</i> <b>{campus_info['Всего мест']}</b>\n"
            campus_text += f"💯 <i>Занято в %:</i> <b>{campus_info['Занято в %']}</b>\n\n"

        await message.answer(campus_text, parse_mode='HTML')
    else:
        await message.answer('<b>Вам необходимо зарегистрироваться '
                             'для выполнения этой команды!</b> ❌', parse_mode='HTML')


@router.message(Command('profile'))
async def cmd_profile(message: Message):
    user = get_user(message.from_user.id)

    if user:
        req = create_request(user)
        profile = req.get_user_info(print_result=False)

        profile_text = "👤 <b>Ваш профиль:</b>\n\n"
        for name, value in profile.items():
            if name == 'Дедлайн':
                goals = value.split('\n')
                profile_text += f"<b>{name}:</b>\n"
                for goal in goals:
                    if goal.strip():
                        profile_text += f"    🎯 <i>{goal.strip()}</i>\n"
            else:
                emoji = {
                    "Логин": "🔐",
                    "Имя на портале": "👤",
                    "Фамилия на портале": "👥",
                    "Уровень": "📊",
                    "Количество peer поинтов": "🤝",
                    "Количество code review поинтов": "🔍",
                    "Количество coins": "💰",
                    "Количество пенальти": "⚖️",
                }
                profile_text += f"{emoji.get(name, '📝')} <b>{name}:</b> {value}\n"

        await message.answer(profile_text, parse_mode='HTML')
    else:
        await message.answer('<b>Вам необходимо зарегистрироваться для '
                             'выполнения этой команды!</b> ❌', parse_mode='HTML')


async def notify_task(message: Message, req: Request):
    while True:
        await asyncio.sleep(300)
        result = req.get_events(print_result=False, only_notify=True)
        if result:
            answer_text = "🔔 <b>Проверка:</b>\n\n"
            answer_text += f"📝 Описание: {result['Описание']}\n"
            answer_text += f"⏰ Начало через: {result['Начало через']}\n\n"

            await message.answer(answer_text, parse_mode='HTML')


@router.message(Command('start_notify'))
async def cmd_start_notify(message: Message):
    user = get_user(message.from_user.id)

    if user:
        if not hasattr(router, 'notify_task'):
            req = create_request(user)
            router.notify_task = asyncio.create_task(notify_task(message, req))
            await message.answer("✅ Уведомления включены.")
        else:
            await message.answer("🚫 Уведомления уже включены.")
    else:
        await message.answer('<b>Вам необходимо зарегистрироваться для'
                             ' выполнения этой команды!</b> ❌', parse_mode='HTML')


@router.message(Command('stop_notify'))
async def cmd_stop_notify(message: Message):
    user = get_user(message.from_user.id)

    if user:
        if hasattr(router, 'notify_task'):
            router.notify_task.cancel()
            del router.notify_task
            await message.answer("⛔️ Уведомления остановлены.")
        else:
            await message.answer("🚫 Уведомления не включены.")
    else:
        await message.answer('<b>Вам необходимо зарегистрироваться '
                             'для выполнения этой команды!</b> ❌', parse_mode='HTML')
