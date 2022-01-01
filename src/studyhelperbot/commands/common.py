from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter

from studyhelperbot.db import StudyHelperBotDB
from studyhelperbot import answers as ans


async def cmd_start(message: types.Message,
                    state: FSMContext,
                    db: StudyHelperBotDB):
    await state.finish()
    tg_user_id = message.from_user.id
    tg_chat_id = message.chat.id
    if not db.row_exists(tg_chat_id, "tg_chat_id", "chats"):
        db.insert_chat_record(tg_chat_id=tg_chat_id,
                              chat_type=message.chat.type)
    if not db.row_exists(tg_user_id):
        db.insert_new_user_account(tg_user_id=tg_user_id,
                                   tg_chat_id=tg_chat_id)
    await message.answer(
        ans.start(),
        reply_markup=types.ReplyKeyboardRemove()
    )


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Canceled", reply_markup=types.ReplyKeyboardRemove())


def register_messages_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
