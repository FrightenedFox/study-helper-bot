import logging
import json
from dataclasses import dataclass
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, executor, types

from studyhelperbot import config
from studyhelperbot import initialize_logging
from studyhelperbot import responses as resp
from studyhelperbot import usosapi
from studyhelperbot import sync_usos_data
from studyhelperbot.db import StudyHelperBotDB


initialize_logging()
bot_params = config("bot")
bot = Bot(bot_params["token"])
dp = Dispatcher(bot)
db = StudyHelperBotDB()


@dataclass
class Permission:
    talk_with_bot = "talk_with_bot"
    list_lectures = "list_lectures"
    list_exams = "list_exams"
    list_stats = "list_stats"
    add_lectures = "add_lectures"
    add_exams = "add_exams"
    accept_lectures = "accept_lectures"
    accept_exams = "accept_exams"
    manage_lectures = "manage_lectures"
    menage_exams = "menage_exams"
    global_sync = "global_sync"
    list_users = "list_users"
    add_users = "add_users"
    remove_users = "remove_users"
    manage_permissions = "manage_permissions"
    list_server_status = "list_server_status"
    list_logs = "list_logs"


async def usos_send_link(message, response, sync_function):
    logging.debug(f"Connecting with USOS: tg_user_id={message.from_user.id}")
    usosapi_params = config("usosapi")
    usos_con = usosapi.USOSAPIConnection(**usosapi_params)
    if usos_con.test_connection():
        url = usos_con.get_authorization_url()
        # TODO: combine into one cool message
        await message.answer(response())
        await message.answer(url)
        other_details = usos_con.get_request_data()
        other_details["sync_function"] = sync_function
        db.set_expected_method(tg_chat_id=message.chat.id,
                               wait_for_answer=True,
                               expected_method="code_from_usos",
                               other_details=json.dumps(other_details))
    else:
        logging.error("Unsuccessful connection with USOS")


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    if not message.from_user.is_bot:
        tg_user_id = message.from_user.id
        tg_chat_id = message.chat.id
        if not db.user_is_banned(tg_user_id):
            # TODO: make different hello messages for existing and new users
            await message.answer(resp.start())
            if not db.row_exists(tg_chat_id, "tg_chat_id", "chats"):
                db.create_chat_record(tg_chat_id=tg_chat_id,
                                      chat_type=message.chat.type)
            if not db.row_exists(tg_user_id):
                db.create_new_user_account(tg_user_id=tg_user_id,
                                           tg_chat_id=tg_chat_id)


@dp.message_handler(commands=["register"])
async def cmd_register(message: types.Message):
    tg_user_id = message.from_user.id
    if db.user_is_verified(tg_user_id):
        await message.answer(resp.you_are_already_registered())
    elif db.user_can(tg_user_id, Permission.talk_with_bot):
        await usos_send_link(message, resp.register, sync_function="user_activation")
    else:
        await message.answer(resp.permission_conflict())


@dp.message_handler(commands=["global_sync"])
async def cmd_global_sync(message: types.Message):
    tg_user_id = message.from_user.id
    if db.user_is_verified(tg_user_id) and db.user_can(tg_user_id, Permission.global_sync):
        await usos_send_link(message, resp.wait_for_link, sync_function="global_sync")
    else:
        await message.answer(resp.permission_conflict())


@dp.message_handler()
async def echo(message: types.Message):
    if not db.user_is_banned(message.from_user.id):
        waiting_for_anwer, expected_method, other_details = db.get_expected_method(message.chat.id)
        if waiting_for_anwer:
            exp_ans = ExpectedAnswers(message, other_details)
            await getattr(exp_ans, expected_method)()
        else:
            await message.answer(resp.unknown_command())


class ExpectedAnswers:  # TODO: rewrite with states
    def __init__(self, message: types.Message, other_details):
        self.message = message
        self.other_details = json.loads(other_details)
        self.tg_chat_id = self.message.chat.id
        self.tg_user_id = self.message.from_user.id

    def clean_message(self):
        return "".join(self.message.text.split())

    async def code_from_usos(self):
        verification_code = self.clean_message()
        usosapi_params = config("usosapi")
        usos_con = usosapi.USOSAPIConnection(**usosapi_params)
        usos_con.set_request_data(
            self.other_details["request_token"],
            self.other_details["request_token_secret"],
        )
        try:
            usos_con.authorize_with_pin(verification_code)
        except usosapi.USOSAPIException:
            await self.message.answer(resp.incorrect_verification_code())
            # TODO: allow for multiple trials
            db.set_expected_method(self.tg_chat_id)
        else:
            await self.message.answer(resp.successful_verification())
            db.set_expected_method(self.tg_chat_id)
            getattr(sync_usos_data, self.other_details["sync_function"])(
                db, self.tg_user_id, usos_con)
            usos_con.logout()
            # TODO: say something in the end xD


if __name__ == "__main__":
    db.connect()
    executor.start_polling(dp, skip_updates=True)
    db.disconnect()

