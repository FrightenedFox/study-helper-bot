import asyncio
import json
import logging
from dataclasses import dataclass

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.rethinkdb import RethinkDBStorage
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.bot_command import BotCommand
from aiogram.types import Message
from aiogram.utils import executor

from studyhelperbot import config
from studyhelperbot import initialize_logging
from studyhelperbot.db import StudyHelperBotDB
from studyhelperbot import register_messages_storytellers
from studyhelperbot import register_messages_common
from studyhelperbot import register_messages_usos_operations


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/overview", description="Quick info about course"),
        BotCommand(command="/register", description="Verify your identity"),
        BotCommand(command="/sync_my_groups",
                   description="Add me to my groups"),
        BotCommand(command="/cancel", description="Cancel any action")
    ]
    await bot.set_my_commands(commands)


class PostgresMiddleware(BaseMiddleware):

    def __init__(self, db):
        self.db = db
        super(PostgresMiddleware, self).__init__()

    async def on_pre_process_message(self, _:types.Message, data: dict):
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

    await set_commands(bot)

    await dp.skip_updates()
    await dp.start_polling()


if __name__ == '__main__':
    initialize_logging()
    db_obj = StudyHelperBotDB()
    db_obj.connect()
    asyncio.run(main(db_obj))
    db_obj.disconnect()
