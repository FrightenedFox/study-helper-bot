import logging
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, timedelta

from studyhelperbot import config, initialize_logging
from studyhelperbot.db import StudyHelperBotDB


initialize_logging()
params = config("bot")
bot = Bot(token=params["token"])    # for now can be rewritten as Bot(**params)
dp = Dispatcher(bot)
db = StudyHelperBotDB()


# TODO: move this garbage to the separate file
help_message = """Witam!
Jestem botem drugiego roku Inżynierii i Analizy Danych na PRz!
Wpisz /help lub !help.
"""

register_message = """Proszę podać swój email PRz dla sprawdzenia osoby.
P.s.: dostęp do tego botu mają ponad 500 000 000 osób, nie mogę dopuszczać każdego -_-  
"""


@dp.message_handler(commands=["start"])
async def cmd_help(message: types.Message):
    if not message.from_user.is_bot:
        tg_user_id = message.from_user.id
        tg_chat_id = message.chat.id
        if not db.user_is_banned(tg_user_id):
            # TODO: make different hello messages for existing and new users
            await message.answer(help_message)
            if not db.row_exists(tg_chat_id, "tg_chat_id", "chats"):
                db.create_chat_record(tg_chat_id=tg_chat_id,
                                      chat_type=message.chat.type)
            if not db.row_exists(tg_user_id):
                db.create_new_user_account(tg_user_id=tg_user_id,
                                           tg_chat_id=tg_chat_id)


@dp.message_handler()
async def echo(message: types.Message):
    waiting_for_ans, exp_method, add_ans_info = db.get_expected_method(message.chat.id)
    # TODO: Add logging here!
    if waiting_for_ans:
        ea = ExpectedAnswers(message, add_ans_info)
        await getattr(ea, exp_method)()
    else:
        await message.answer("Sorki, ale nie wiem co ci odpisać :o")


class ExpectedAnswers:
    def __init__(self, message: types.Message, other_details):
        self.message = message
        self.additional_info = other_details
        self.tg_user_id = db.get_user_id("tg_user_id", self.message.from_user.id)

    def clean_message(self):
        return "".join(self.message.text.split())


if __name__ == "__main__":
    db.connect()
    executor.start_polling(dp, skip_updates=True)
    db.disconnect()
