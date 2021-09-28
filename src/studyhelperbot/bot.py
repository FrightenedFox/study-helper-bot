import logging
from aiogram import Bot, Dispatcher, executor, types
from studyhelperbot.config import config
import studyhelperbot.handlers


params = config("telegram")
bot = Bot(token=params["token"])    # for now can be rewritten as Bot(**params)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

help_message = """Witam!
Jestem botem drugiego roku Inżynierii i Analizy Danych na PRz!
Wpisz ```/help``` lub ```!help```.
"""


@dp.message_handler(commands=["start", "help", "s", "h"])
async def cmd_help(message: types.Message):
    await message.answer(help_message)


@dp.message_handler(commands="newEvent")
async def cmd_test1(message: types.Message):
    await message.reply("")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
