from contextlib import suppress

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

from studyhelperbot import answers as ans
from studyhelperbot.db import StudyHelperBotDB
import studyhelperbot.commands.keyboards as kb

cb_commits = CallbackData("commit", "action")
cb_courses = CallbackData("courses", "course_id")


class CommitStates(StatesGroup):
    some_state = State()


async def cmd_commit(message: types.Message, state: FSMContext):
    await state.finish()
    available_commits = {
        "add_activity": {"pl": "Streszczenie zajęć"},
        "add_test":     {"pl": "Informacja o teście"},
    }
    await message.answer(ans.choose_commits(),
                         reply_markup=kb.get_commits_keyboard(
                             available_commits, cb_commits))


async def add_activity_callback(call: types.CallbackQuery,
                                callback_data: dict,
                                state: FSMContext,
                                db: StudyHelperBotDB):
    courses_df = db.get_all_user_courses(call.from_user.id)
    await call.message.edit_text(ans.choose_request("courses"))
    await call.message.edit_reply_markup(kb.get_courses_keyboard(
            courses_df.course_name, courses_df.course_id, cb_courses))
    with suppress(MessageNotModified):  # Empty inline keyboard
        await call.message.edit_reply_markup()
    await call.answer()


def register_messages_commits(dp: Dispatcher):
    dp.register_message_handler(cmd_commit, commands="commit", state="*")
