from aiogram import Bot, Dispatcher

from SchoolParser.SchoolRequests import Request
from Bot.handlers import auth_handlers, main_handlers



class TgBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)

        self.dp = Dispatcher()
        self.dp.include_routers(main_handlers.router, auth_handlers.router)

    async def start_bot(self):
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)
