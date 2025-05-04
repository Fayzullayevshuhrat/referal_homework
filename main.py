import asyncio
import logging
import sys
import json

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.utils.deep_linking import create_start_link
from config import  TOKEN
data = {}


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

def load():
    with open("users.json", "r") as file:
        data = json.load(file)

    return data

def write(data):
    with open("users.json", "w") as file:
        json.dump(data, file, indent=4)

@dp.message(CommandStart())
async def command_start_handler(message: Message, command: CommandObject) -> None:
    data = load()
    data[message.from_user.id] = 0
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
    ref_id = command.args
    if ref_id:
        data[ref_id] = data.get(ref_id, 0) + 1
        await message.answer(f"Siz shu userdan referal olgansiz {ref_id}")
    write(data)

@dp.message(Command("refer"))
async def echo_handler(message: Message) -> None:
    link = await create_start_link(bot=bot, payload=str(message.from_user.id))

    await message.answer(link)

@dp.message(Command("count"))
async def echo_handler(message: Message) -> None:
    data = load()
    cnt = data.get(message.from_user.id, 0) + 1
    await message.answer(f"{cnt}")

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())