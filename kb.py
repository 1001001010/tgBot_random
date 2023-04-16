from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

cancellation = types.InlineKeyboardMarkup(row_width=2)
cancellation.add(types.InlineKeyboardButton(text="Отмена", callback_data="cancellation"))

buttons = types.InlineKeyboardMarkup(row_width=1)
buttons.add(types.InlineKeyboardButton(text="Учавствовать", callback_data="Participate"))

send = types.InlineKeyboardMarkup(row_width=1)
send.add(types.InlineKeyboardButton(text="Отправить", callback_data="send"))

Participate = types.InlineKeyboardMarkup(row_width=1)
Participate.add(types.InlineKeyboardButton(text="Учавствовать", callback_data="Participate2"))

Complete = types.InlineKeyboardMarkup(row_width=1)
Complete.add(types.InlineKeyboardButton(text="Завершить досрочно", callback_data="Complete"))

close = types.InlineKeyboardMarkup(row_width=1)
close.add(types.InlineKeyboardButton(text="Проверить результаты", url = "https://t.me/tteeesssst_bot"))

like = types.InlineKeyboardMarkup(row_width=1)
like.add(types.InlineKeyboardButton(text="Вы участник", callback_data="like"))