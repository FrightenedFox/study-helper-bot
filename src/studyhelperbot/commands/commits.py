import datetime as dt
from contextlib import suppress

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

import studyhelperbot.commands.keyboards as kb
from studyhelperbot import answers as ans
from studyhelperbot.db import StudyHelperBotDB

cb_commits = CallbackData("commit", "action")
cb_courses = CallbackData("course_to_commit", "course_id")
cb_add_activity = CallbackData("add_activity", "activity_id")


class AddActivityStates(StatesGroup):
    wait_for_date = State()


async def cmd_commit(message: types.Message, state: FSMContext):
    await state.finish()
    available_commits = {
        "add_activity": "Streszczenie zajęć",
        "add_test": "Informacja o teście",
    }
    await message.answer(ans.choose_commits(),
                         reply_markup=kb.get_column_keyboard(
                             values_dict=available_commits,
                             callback_name=cb_commits,
                             callback_key="action"
                         ))


async def commit_type_callback(call: types.CallbackQuery,
                               callback_data: dict,
                               state: FSMContext,
                               db: StudyHelperBotDB):
    action = callback_data["action"]
    await state.update_data({"action": action})
    if action in ["add_activity", "add_test"]:
        courses_df = db.get_all_user_courses(call.from_user.id)
        await call.message.edit_text(ans.choose_request("courses"))
        await call.message.edit_reply_markup(kb.get_courses_keyboard(
            courses_df.course_name, courses_df.course_id,
            cb_courses, all_courses_button=False))
        await call.answer()


async def course_to_commit_callback(call: types.CallbackQuery,
                                    callback_data: dict,
                                    state: FSMContext,
                                    db: StudyHelperBotDB):
    course_id = callback_data["course_id"]
    await state.update_data({"course_id": course_id})
    await call.message.edit_text(ans.enter_date())
    with suppress(MessageNotModified):  # Empty inline keyboard
        await call.message.edit_reply_markup()
    await AddActivityStates.wait_for_date.set()
    await call.answer()


async def get_date(message: types.Message,
                   state: FSMContext,
                   db: StudyHelperBotDB):
    try:
        date = dt.datetime.strptime(message.text, "%d.%m.%Y")
    except ValueError:
        await message.reply(ans.incorrect_date())
    else:
        user_data = await state.get_data()
        results_df = db.get_user_activities_details(
            message.from_user.id,
            start_date=date.strftime("%Y-%m-%d"),
            end_date=(date + dt.timedelta(days=1)).strftime("%Y-%m-%d"),
            course_id=user_data["course_id"]
        )
        if results_df.shape[0] > 0:
            options = {
                res.activity_id: (f"{res.group_type} {res.group_number} "
                                  f"{res.start_time.time().strftime('%H:%M')}-"
                                  f"{res.end_time.time().strftime('%H:%M')}")
                for ind, res in results_df.iterrows()
            }
            answer = ans.choose_from_results(
                results_df.loc[0, "course_name"],
                results_df.loc[0, "start_time"].date().strftime("%a, %d %b %Y")
            )
            await message.answer(answer,
                                 reply_markup=kb.get_column_keyboard(
                                     values_dict=options,
                                     callback_name=cb_add_activity,
                                     callback_key="activity_id"
                                 ),
                                 parse_mode=types.ParseMode.MARKDOWN_V2)

        await message.reply("Hi")
        pass


def register_messages_commits(dp: Dispatcher):
    dp.register_message_handler(cmd_commit, commands="commit", state="*")
    dp.register_callback_query_handler(commit_type_callback,
                                       cb_commits.filter(),
                                       state="*")
    dp.register_callback_query_handler(course_to_commit_callback,
                                       cb_courses.filter(),
                                       state="*")
    dp.register_message_handler(get_date, state=AddActivityStates.wait_for_date)
