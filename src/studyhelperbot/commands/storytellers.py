from contextlib import suppress
from math import ceil
import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import IDFilter
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

from studyhelperbot import answers as ans
from studyhelperbot.db import StudyHelperBotDB

localizations = {
    "all_courses": {"pl": "Wszystkie przedmioty",
                    "en": "All courses"},
    "to_the_end": {"pl": "Do końca semestru",
                   "en": "Until the end of the semester"}
}

n_days_types = [1, 2, 3, 7, 14, 30]
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
        tg_user_id, end_date, course_id)
    return ans.storytellers_overview(activities_result)


def get_days_keyboard(n_cols=2):
    keyboard = types.InlineKeyboardMarkup(row_width=n_cols)

    # Add "ALL" button at the first row
    keyboard.insert(types.InlineKeyboardButton(
        text=localizations["to_the_end"]["pl"],
        callback_data=cb_days.new(n_days="NULL")
    ))
    keyboard.row()

    n_rows = ceil(len(n_days_types) / n_cols)
    for row_id in range(n_rows):
        start = row_id * n_cols
        stop = (row_id + 1) * n_cols
        stop = len(n_days_types) if stop > len(n_days_types) else stop
        for n_days in n_days_types[start:stop]:
            keyboard.insert(types.InlineKeyboardButton(
                text=str(n_days),
                callback_data=cb_days.new(n_days=n_days)
            ))
        keyboard.row()
    return keyboard


def get_courses_keyboard(courses, course_ids, n_cols=2):
    keyboard = types.InlineKeyboardMarkup(row_width=n_cols)

    # Add "ALL" button at the first row
    keyboard.insert(types.InlineKeyboardButton(
        text=localizations["all_courses"]["pl"],
        callback_data=cb_courses.new(course_id="NULL")
    ))
    keyboard.row()

    n_rows = ceil(len(courses) / n_cols)
    for row_id in range(n_rows):
        start = row_id * n_cols
        stop = (row_id + 1) * n_cols
        stop = len(courses) if stop > len(courses) else stop
        for course_id, course in zip(course_ids[start:stop],
                                     courses[start:stop]):
            keyboard.insert(types.InlineKeyboardButton(
                text=str(course),
                callback_data=cb_courses.new(course_id=course_id)
            ))
        keyboard.row()
    return keyboard


async def overview(message: types.Message, db: StudyHelperBotDB):
    courses = db.get_all_user_courses(message.from_user.id)
    courses_ids = [course[0] for course in courses]
    courses_names = [course[1] for course in courses]
    await message.answer(
        ans.choose_storytellers("courses"),
        reply_markup=get_courses_keyboard(courses_names, courses_ids)
    )


async def course_change_callback(call: types.CallbackQuery,
                                 callback_data: dict,
                                 state: FSMContext):
    course_id = callback_data["course_id"]
    await state.update_data({"course_id": course_id})
    await call.message.edit_text(ans.choose_storytellers("days"))
    await call.message.edit_reply_markup(get_days_keyboard())
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

