import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.deep_linking import get_start_link, decode_payload
from config import TOKEN

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER PRIMARY KEY,
        invited_by INTEGER
    )
""")
conn.commit()

def add_user(chat_id, invited_by=None):
    cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (chat_id, invited_by) VALUES (?, ?)", (chat_id, invited_by))
        conn.commit()

def has_been_invited(chat_id):
    cursor.execute("SELECT invited_by FROM users WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    return result and result[0] is not None

# handlers

@dp.message(CommandStart(deep_link=True))
async def start_handler(message: types.Message, command: CommandStart):
    user_id = message.from_user.id
    payload = command.args
    if payload:
        invited_by = int(decode_payload(payload))
        if invited_by != user_id and not has_been_invited(user_id):
            add_user(user_id, invited_by)
            await message.answer(f"✅ Siz referal orqali kirdingiz! Sizni taklif qilgan: <b>{invited_by}</b>")
        else:
            add_user(user_id)
            await message.answer("⚠ Siz allaqachon referal bo‘lgansiz yoki o‘zingizning havolangizdan foydalandingiz.")
    else:
        add_user(user_id)
        await message.answer("👋 Salom! Oddiy /start orqali kirdingiz.")

    # buttons
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=" Mening referal havolam", callback_data="get_link")],
            [InlineKeyboardButton(text=" Referal do‘stlarim soni", callback_data="my_referrals")]
        ]
    )
    await message.answer("Quyidagi tugmalar orqali harakat qiling:", reply_markup=keyboard)

@dp.callback_query(F.data == "get_link")
async def get_referal_link(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    deep_link = await get_start_link(payload=str(user_id), encode=True)
    await callback.message.answer(f" Sizning referal havolangiz:\n{deep_link}")

@dp.callback_query(F.data == "my_referrals")
async def show_referrals(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cursor.execute("SELECT COUNT(*) FROM users WHERE invited_by = ?", (user_id,))
    count = cursor.fetchone()[0]
    await callback.message.answer(f" Siz {count} ta do‘stingizni taklif qildingiz!")



async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
