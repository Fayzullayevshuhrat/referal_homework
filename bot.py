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

TOKEN = "7828936588:AAH_6TBsJjcRyZ6YP-SyQEmotO4_xfHMDWw"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

def load():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def write(data):
    with open("users.json", "w") as file:
        json.dump(data, file, indent=4)

@dp.message(CommandStart())
async def command_start_handler(message: Message, command: CommandObject) -> None:
    user_id = str(message.from_user.id)
    data = load()

    if user_id not in data:
        data[user_id] = {
            "full_name": message.from_user.full_name,
            "username": message.from_user.username,
            "language_code": message.from_user.language_code,
            "is_bot": message.from_user.is_bot,
            "ref_count": 0
        }

        if command.args:
            ref_id = command.args
            if ref_id != user_id and ref_id in data:
                data[ref_id]["ref_count"] += 1
                await message.answer(f"Siz {ref_id} foydalanuvchi orqali keldingiz!")

    write(data)
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

@dp.message(Command("refer"))
async def refer_handler(message: Message) -> None:
    link = await create_start_link(bot=bot, payload=str(message.from_user.id))
    await message.answer(f"Referal havolangiz:\n{link}")

@dp.message(Command("count"))
async def count_handler(message: Message) -> None:
    user_id = str(message.from_user.id)
    data = load()
    ref_count = data.get(user_id, {}).get("ref_count", 0)
    await message.answer(f"Sizning referal havolangiz orqali {ref_count} kishi keldi.")

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())