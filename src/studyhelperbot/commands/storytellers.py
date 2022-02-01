import datetime as dt
from contextlib import suppress

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

from studyhelperbot import answers as ans
from studyhelperbot.db import StudyHelperBotDB
import studyhelperbot.commands.keyboards as kb

cb_days = CallbackData("days", "n_days")
cb_courses = CallbackData("courses", "course_id")


def answer_overview(tg_user_id, course_id,
                    n_days, db: StudyHelperBotDB):
    if n_days == "NULL":
        end_date = None
    else:
        end_date = dt.date.isoformat(
            dt.date.today() + dt.timedelta(days=int(n_days)))
    if course_id == "NULL":
        course_id = None
    activities_result = db.get_user_activities_details(
        tg_user_id=tg_user_id, end_date=end_date, course_id=course_id)
    return ans.storytellers_overview(activities_result)


async def overview(message: types.Message, db: StudyHelperBotDB):
    courses_df = db.get_all_user_courses(message.from_user.id)
    await message.answer(
        ans.choose_request("course"),
        reply_markup=kb.get_courses_keyboard(
            courses_df.course_name, courses_df.course_id, cb_courses)
    )


async def course_change_callback(call: types.CallbackQuery,
                                 callback_data: dict,
                                 state: FSMContext):
    course_id = callback_data["course_id"]
    await state.update_data({"course_id": course_id})
    await call.message.edit_text(ans.choose_request("day"))
    await call.message.edit_reply_markup(kb.get_days_keyboard(cb_days))
    await call.answer()


async def day_change_callback(call: types.CallbackQuery,
                              callback_data: dict,
                              state: FSMContext,
                              db: StudyHelperBotDB):
    n_days = callback_data["n_days"]
    await state.update_data({"n_days": n_days})
    user_data = await state.get_data()
    answer = answer_overview(call.from_user.id, user_data["course_id"],
                             user_data["n_days"], db)
    await call.message.edit_text(answer, parse_mode=types.ParseMode.MARKDOWN_V2)
    with suppress(MessageNotModified):  # Empty inline keyboard
        await call.message.edit_reply_markup()
    await call.answer()


def register_messages_storytellers(dp: Dispatcher):
    dp.register_message_handler(overview, commands="overview", state="*")
    dp.register_callback_query_handler(course_change_callback,
                                       cb_courses.filter(),
                                       state="*")
    dp.register_callback_query_handler(day_change_callback,
                                       cb_days.filter(),
                                       state="*")
