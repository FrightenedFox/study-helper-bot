import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.rethinkdb import RethinkDBStorage
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types.bot_command import BotCommand

from studyhelperbot import config
from studyhelperbot import initialize_logging
from studyhelperbot import register_messages_commits
from studyhelperbot import register_messages_common
from studyhelperbot import register_messages_storytellers
from studyhelperbot import register_messages_usos_operations
from studyhelperbot.db import StudyHelperBotDB


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="/overview", description="Quick info about course"),
        BotCommand(
            command="/commit", description="Add some info to the database"),
        BotCommand(
            command="/register", description="Verify your identity"),
        BotCommand(
            command="/sync_my_groups", description="Add me to my groups"),
        BotCommand(
            command="/cancel", description="Cancel any action")
    ]
    await bot.set_my_commands(commands)


class PostgresMiddleware(BaseMiddleware):

    def __init__(self, db):
        self.db = db
        super(PostgresMiddleware, self).__init__()

    async def on_pre_process_message(self, _: types.Message, data: dict):
        data["db"] = self.db

    async def on_pre_process_callback_query(self, _: types.CallbackQuery,
                                            data: dict):
        data["db"] = self.db


async def main(db: StudyHelperBotDB):
    bot_params = config("bot")
    bot = Bot(bot_params["token"])
    rethinkdb_params = config("rethinkdb")
    storage = RethinkDBStorage(**rethinkdb_params)
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(PostgresMiddleware(db))

    register_messages_common(dp)
    register_messages_storytellers(dp)
    register_messages_usos_operations(dp)
    register_messages_commits(dp)

    await set_commands(bot)

    await dp.skip_updates()
    await dp.start_polling()

    await storage.close()
    await storage.wait_closed()


if __name__ == '__main__':
    initialize_logging()
    db_obj = StudyHelperBotDB()
    db_obj.connect()
    asyncio.run(main(db_obj))
    db_obj.disconnect()
