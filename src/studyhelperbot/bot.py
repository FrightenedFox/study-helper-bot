import logging
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, timedelta

from studyhelperbot import config
from studyhelperbot.db import StudyHelperBotDB


params = config("telegram")
bot = Bot(token=params["token"])    # for now can be rewritten as Bot(**params)
dp = Dispatcher(bot)
db = StudyHelperBotDB()
logging.basicConfig(level=logging.INFO)

# TODO: move this garbage to the separate file
help_message = """Witam!
Jestem botem drugiego roku Inżynierii i Analizy Danych na PRz!
Wpisz ```/help``` lub ```!help```.
"""

register_message = """Proszę podać swój email PRz dla sprawdzenia osoby.
P.s.: dostęp do tego botu mają ponad 500 000 000 osób, nie mogę dopuszczać każdego -_-  
"""


@dp.message_handler(commands=["start"])
async def cmd_help(message: types.Message):
    if not message.from_user.is_bot:
        telegram_id = message.from_user.id
        chat_id = message.chat.id
        if not db.user_is_banned(telegram_id):
            # TODO: make different hello messages for existing and new users
            await message.answer(help_message)
            if not db.record_exists(chat_id, "chat_id", "chats"):
                db.create_chat_record(chat_id=chat_id,
                                      chat_type=message.chat.type)
            if not db.record_exists(telegram_id):
                db.create_new_user_account(telegram_id=telegram_id,
                                           bot_chat_id=chat_id)


@dp.message_handler(commands=["register"])
async def cmd_register(message: types.Message):
    # TODO: add function which check whether user already has an email
    #       and if so - forbids to register, only change email;
    await message.answer(register_message)
    db.set_expected_method(chat_id=message.chat.id,
                           wait_for_answer=True,
                           expected_method="send_email")
    # TODO: limit number of registrations per user


@dp.message_handler()
async def echo(message: types.Message):
    waiting_for_ans, exp_method, add_ans_info = db.get_expected_method(message.chat.id)
    # TODO: Add logging here!
    if waiting_for_ans:
        ea = ExpectedAnswers(message, add_ans_info)
        await getattr(ea, exp_method)()
    else:
        await message.answer("Sorki, ale nie wiem co ci odpisać :o")


# @dp.message_handler(commands="newEvent")
# async def cmd_test1(message: types.Message):
#     await message.reply("")


class ExpectedAnswers:
    def __init__(self, message: types.Message, additional_answer_info):
        self.message = message
        self.additional_info = additional_answer_info
        self.user_dbid = db.get_user_id("telegram_id", self.message.from_user.id)

    def clean_message(self):
        return "".join(self.message.text.split())

    async def send_email(self):
        message_without_whitespaces = self.clean_message()
        verification_id = await studyhelperbot.registration.add_email_task(
            recipient_user_id=self.user_dbid,
            recipient_email=message_without_whitespaces,
        )
        # TODO: create exception handling
        await self.message.answer(
            "Do ciebie został wysłany email z kodem weryfikacji."
            "Proszę wpisać go w ciągu następujących 10 minut."
        )
        db.set_expected_method(chat_id=self.message.chat.id,
                               wait_for_answer=True,
                               expected_method="verify_code",
                               additional_answer_info=verification_id)

    async def verify_code(self):
        user_answer = self.clean_message()
        verification_id = int(self.additional_info)
        true_password, datetime_expires, used_email = db.\
            get_user_verification_record(verification_id)
        if datetime.utcnow() <= datetime_expires and user_answer == true_password:
            await self.message.answer("Password is correct!")
            db.set_specific_column(
                where="user_id",        # Add email
                where_value=self.user_dbid,
                col_name="email",
                col_name_value=used_email,
                table="users",
            )
            db.set_specific_column(     # Update priority level
                where="user_id",
                where_value=self.user_dbid,
                col_name="priority_level",
                col_name_value=10,
                table="users",
            )
        else:
            await self.message.answer("Password is wrong!!!")
        # Reset expected method
        db.set_expected_method(chat_id=self.message.chat.id)


if __name__ == "__main__":
    db.connect()
    executor.start_polling(dp, skip_updates=True)
    db.disconnect()
