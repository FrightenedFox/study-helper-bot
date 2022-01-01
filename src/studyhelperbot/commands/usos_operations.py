import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.dispatcher.filters.state import State, StatesGroup

from studyhelperbot.db import StudyHelperBotDB
from studyhelperbot import answers as ans
from studyhelperbot import usosapi
from studyhelperbot import config
from studyhelperbot import sync_usos_data


class VerifyAndSync(StatesGroup):
    wait_for_code = State()


async def usos_send_link(message: types.Message,
                         answer: ans,
                         state: FSMContext,
                         sync_function: str):
    logging.debug(f"Connecting with USOS: tg_user_id={message.from_user.id}")
    usosapi_params = config("usosapi")
    usos_con = usosapi.USOSAPIConnection(**usosapi_params)
    if usos_con.test_connection():
        url = usos_con.get_authorization_url()
        # TODO: combine into one cool message
        usos_request_data = usos_con.get_request_data()
        await state.update_data({
            "request_token": usos_request_data["request_token"],
            "request_token_secret": usos_request_data["request_token_secret"],
            "sync_function": sync_function,
        })
        await message.answer(answer(url))
        await VerifyAndSync.wait_for_code.set()
    else:
        logging.error("Unsuccessful connection with USOS")
        # TODO: tell user something is wrong with connection and the problem
        #  is on the side of the server
        await message.answer("Bad luck!")
        await state.finish()


async def start_registration(message: types.Message,
                             state: FSMContext,
                             db: StudyHelperBotDB):
    tg_user_id = message.from_user.id
    if db.user_is_verified(tg_user_id):
        await message.answer(ans.you_are_already_registered())
    else:
        await usos_send_link(message=message, answer=ans.register,
                             state=state, sync_function="verify_user")


async def sync_users_groups(message: types.Message,
                      state: FSMContext,
                      db: StudyHelperBotDB):
    if db.user_is_verified(message.from_user.id):
        await usos_send_link(message=message, answer=ans.register,
                             state=state, sync_function="sync_users_groups")


async def sync_course(message: types.Message,
                      state: FSMContext,
                      db: StudyHelperBotDB):
    commands_dict = {
        "/sync_activities": "sync_activities",
        "/sync_course_groups": "sync_course_groups"
    }
    if db.user_is_verified(message.from_user.id):
        await usos_send_link(message=message,
                             answer=ans.register,
                             state=state,
                             sync_function=commands_dict[message.text])


async def usos_check_code(message: types.Message,
                          state: FSMContext,
                          db: StudyHelperBotDB):
    pincode = "".join(message.text.split())
    usosapi_params = config("usosapi")
    usos_con = usosapi.USOSAPIConnection(**usosapi_params)
    user_data = await state.get_data()
    usos_con.set_request_data(
        user_data["request_token"],
        user_data["request_token_secret"],
    )
    try:
        usos_con.authorize_with_pin(pincode)
    except usosapi.USOSAPIException:
        await message.answer(ans.incorrect_verification_code())
        # TODO: allow for multiple trials
        await state.finish()
    else:
        await message.answer(ans.successful_verification())
        await getattr(
            sync_usos_data, user_data["sync_function"]
        )(db, message.from_user.id, usos_con)
        usos_con.logout()
        await state.finish()
        # TODO: say something in the end xD


def register_messages_usos_operations(dp: Dispatcher):
    dp.register_message_handler(start_registration,
                                commands="register",
                                state="*")
    dp.register_message_handler(sync_course,
                                commands=["sync_activities",
                                          "sync_course_groups"],
                                state="*")
    dp.register_message_handler(sync_users_groups,
                                commands="sync_my_groups",
                                state="*")
    dp.register_message_handler(usos_check_code,
                                state=VerifyAndSync.wait_for_code)
