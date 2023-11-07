import environs
import asyncio

from Bot.bot import TgBot
import connect_db

if __name__ == '__main__':
    env = environs.Env()
    env.read_env()

    connect_db.Base.metadata.create_all(bind=connect_db.engine)

    bot = TgBot(token=env('token'))
    asyncio.run(bot.start_bot())
