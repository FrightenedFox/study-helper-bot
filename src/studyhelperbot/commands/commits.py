from contextlib import suppress
from math import ceil
import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import IDFilter
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified
from aiogram.dispatcher.filters.state import State, StatesGroup

from studyhelperbot import answers as ans
from studyhelperbot.db import StudyHelperBotDB
from studyhelperbot.commands.storytellers import get_courses_keyboard

cb_commits = CallbackData("commit", "action")


class CommitStates(StatesGroup):
    wait_for_code = State()


def get_commits_keyboard(commit_types, n_cols=1):
    # TODO: if n_cols is still == 1 and it is the best option -> rewrite
    #  this function, since it can be implemented much much easily
    keyboard = types.InlineKeyboardMarkup(row_width=n_cols)

    n_rows = ceil(len(commit_types) / n_cols)
    for row_id in range(n_rows):
        start = row_id * n_cols
        stop = (row_id + 1) * n_cols
        stop = len(commit_types) if stop > len(commit_types) else stop
        actions, names = list(commit_types), list(commit_types.values())
        for action, name in zip(actions[start:stop], names[start:stop]):
            keyboard.insert(types.InlineKeyboardButton(
                text=name["pl"],
                callback_data=cb_commits.new(action=action)
            ))
        keyboard.row()
    return keyboard


async def cmd_commit(message: types.Message, state: FSMContext):
    await state.finish()
    available_commits = {
        "add_activity": {"pl": "Streszczenie zajęć"},
        # "add_test":     {"pl": "Informacja o teście"},
    }
    await message.answer(ans.choose_commits(),
                         reply_markup=get_commits_keyboard(available_commits))


def register_messages_commits(dp: Dispatcher):
    dp.register_message_handler(cmd_commit, commands="commit", state="*")
