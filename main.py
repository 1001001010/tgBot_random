import asyncio
import logging
from aiogram import Bot, Dispatcher, types
import configparser
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from kb import *
import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime
import time
from aiogram.types import ContentType, Message

con = sqlite3.connect("data.db")
cur = con.cursor()
config = configparser.ConfigParser()
storage = MemoryStorage()
config.read('config.ini')
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config['settings']['TOKEN'])
dp = Dispatcher(bot, storage=storage)

cur.execute("""CREATE TABLE IF NOT EXISTS draw(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   prize TEXT,
   text TEXT,
   winners INT,
   photo_id
   );
""")

cur.execute("""CREATE TABLE IF NOT EXISTS users(
   id INT,
   number INT,
   UNIQUE ("id") ON CONFLICT IGNORE
   );
""")
cur.execute("""CREATE TABLE IF NOT EXISTS msg_id(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   msg_id TEXT,
   UNIQUE ("msg_id") ON CONFLICT IGNORE
   );
""")
cur.execute("""CREATE TABLE IF NOT EXISTS history(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   prize TEXT,
   text TEXT,
   winners INT,
   number INT
   );
""")


con.commit()

class UserState(StatesGroup):
	prize = State()
	text = State()
	winner = State()
	photo = State()

@dp.message_handler(commands = ("start"))
async def cmd_start(message: types.Message):
	if message.from_user.id == int(config['settings']['admin_id']):
		main_menu_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
		button1 = KeyboardButton('Создать розыгрыш 🎁')
		button2 = KeyboardButton('Мои розыгрыши 🗒')
		main_menu_admin.add(button1, button2)
		await bot.send_message(message.from_user.id, text = 'Привет! Воспользуйся меню ниже', reply_markup=main_menu_admin)
	else:
		ing = str(con.execute(f"SELECT id FROM history ORDER BY id DESC LIMIT 1").fetchone())
		ing  = ing.replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		id_ = str(con.execute(f'SELECT id FROM history WHERE id = {int(ing)}').fetchone())
		id_  = id_ .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		winner = str(con.execute(f'SELECT winners FROM history WHERE id = {int(ing)}').fetchone())
		winner  = winner .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		prize = str(con.execute(f'SELECT prize FROM history WHERE id = {int(ing)}').fetchone())
		prize  = prize.replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		text = str(con.execute(f'SELECT text FROM history WHERE id = {int(ing)}').fetchone())
		text  = text .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		num = str(con.execute(f'SELECT number FROM history WHERE id = {int(ing)}').fetchone())
		num  = num .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		await bot.send_message(message.from_user.id, f"Итоги последнего розыгрыша:\n🆔id: {id_}\n🎁Приз: {prize}\n📢{text}\nКолличество участников: {num}\n👑Победитель: {winner}")
	# await bot.send_message(int(config['settings']['channel_id']), text = 'Привет!')

@dp.message_handler(content_types=ContentType.PHOTO)
async def send_photo_file_id(message: Message):
	await message.reply(message.photo[-1].file_id)

@dp.message_handler(lambda message: message.text == "Создать розыгрыш 🎁")
async def without_puree(message: types.Message):
	await bot.send_message(message.from_user.id, text='**Создание розыгрыша**\n\n✉️ Отправьте текст для розыгрыша.', reply_markup=cancellation, parse_mode='MARKDOWN')
	await UserState.text.set()

@dp.message_handler(lambda message: message.text == "Мои розыгрыши 🗒")
async def canal(message: types.Message):
		sqlite_select_query = ("""SELECT * from history""")
		cur.execute(sqlite_select_query)
		records = cur.fetchall()
		for row in records:
			await bot.send_message(message.from_user.id, f"📖История\nВсего строк:, {len(records)}\n📅всю историю вы можете найти в бд(таблица history)\n🆔id: {row[0]}\n🎁Приз: {row[1]}\n📢Текст: {row[2]}\n👑Победитель: {row[3]}\n📄Колличество участников: {row[4]}")

@dp.message_handler(state=UserState.text)
async def get_text(message: types.Message, state: FSMContext):
	await state.update_data(text=message.text)
	await bot.send_message(message.from_user.id, text='✅ Текст добавлен', parse_mode='MARKDOWN')
	await bot.send_message(message.from_user.id, text='🎁Введите приз', parse_mode='MARKDOWN')
	await UserState.prize.set()
	
@dp.message_handler(state=UserState.prize)
async def get_prize(message: types.Message, state: FSMContext):
	await state.update_data(prize=message.text)
	await bot.send_message(message.from_user.id, text='✅ Приз добавлен', parse_mode='MARKDOWN')
	await message.answer("👑Отлично! Теперь введите победителя через @")
	await UserState.winner.set()	

@dp.message_handler(state=UserState.winner)
async def get_winner(message: types.Message, state: FSMContext):
	await state.update_data(winner=message.text)
	await bot.send_message(message.from_user.id, text='✅ Приз добавлен', parse_mode='MARKDOWN')
	await message.answer("👑Отлично! Введите айди фото")
	await UserState.photo.set()

@dp.message_handler(state=UserState.photo)
async def get_winner(message: types.Message, state: FSMContext):
	await state.update_data(photo=message.text)
	data = await state.get_data()
	await message.answer(f"❗Внимание Розыгрыш!\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n🎁Приз: {data['prize']}\n📢{data['text']}\n\nЭтой информации не видно↓\n\n👑Победитель - {data['winner']}, \n❗Если какие-то данные неверны, то начните сначал", reply_markup=send)
	user_list = (data['prize'], data['text'], data['winner'], data['photo'])
	cur.execute('INSERT INTO draw ("prize", "text", "winners", photo_id) VALUES(?, ?, ?, ?)', user_list) 
	con.commit()
	await state.finish()


@dp.callback_query_handler()
async def call_handler(call: types.CallbackQuery):
	if call.data == 'cancellation':
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		if call.from_user.id == int(config['settings']['admin_id']):
			main_menu_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
			button1 = KeyboardButton('Создать розыгрыш 🎁')
			button2 = KeyboardButton('Мои розыгрыши 🗒')
			button3 = KeyboardButton('Мои каналы 📢')
			main_menu_admin.add(button1, button2)
			main_menu_admin.add(button3)
			await bot.send_message(call.from_user.id, text = 'Отмененно! Воспользуйся меню ниже', reply_markup=main_menu_admin)
	if call.data == 'send':
		ing = str(con.execute(f"SELECT id FROM draw ORDER BY id DESC LIMIT 1").fetchone())
		ing  = ing.replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		prize = str(con.execute(f'SELECT prize FROM draw WHERE id = "{int(ing)}"').fetchone())
		prize  = prize.replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		text = str(con.execute(f'SELECT text FROM draw WHERE id = {int(ing)}').fetchone())
		text  = text .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		photo_id = str(con.execute(f'SELECT photo_id FROM draw WHERE id = {int(ing)}').fetchone())
		photo_id  = photo_id .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		msg = await bot.send_photo(int(config['settings']['channel_id']), photo = photo_id, caption = f"❗Внимание Розыгрыш!\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n🎁Приз: {prize}\n📢{text}", reply_markup=Participate)
		cur.execute('INSERT INTO msg_id ("msg_id")VALUES(?)', (msg.message_id, ))
		con.commit()
		await bot.send_message(call.from_user.id, f"❗Внимание Розыгрыш!\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n🎁Приз: {prize}\n📢{text}", reply_markup=Complete)		
	if call.data == 'Participate2':
		list = (call.from_user.id, "0")
		cur.execute('INSERT INTO users VALUES(?, ?)', list)
		con.commit()
		await bot.answer_callback_query(callback_query_id=call.id,text='Вы учавствуте в розыгрыше', show_alert=True)
		while True:
			cur.execute("select * from users")
			results = cur.fetchall()
			msg1 = str(con.execute(f'SELECT msg_id FROM msg_id').fetchone())
			msg1  = msg1 .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
			winner = str(con.execute(f'SELECT winners FROM draw').fetchone())
			winner  = winner .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
			prize = str(con.execute(f'SELECT prize FROM draw WHERE id = 1').fetchone())
			prize  = prize.replace('(', '').replace(')', '').replace(',', '').replace("'", '')
			text = str(con.execute(f'SELECT text FROM draw WHERE id = 1').fetchone())
			text  = text .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
			photo_id = str(con.execute(f'SELECT photo_id FROM draw WHERE id = 1').fetchone())
			photo_id  = photo_id .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
			await call.bot.edit_message_caption(caption=f"❗Внимание Розыгрыш!\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n🎁Приз: {prize}\n📢{text}\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nКолличество участников: {len(results)}",chat_id=int(config['settings']['channel_id']), message_id=int(msg1), reply_markup=like)
			time.sleep(10)
	if call.data == 'Complete':
		ing = str(con.execute(f"SELECT id FROM draw ORDER BY id DESC LIMIT 1").fetchone())
		ing  = ing.replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		msg1 = str(con.execute(f'SELECT msg_id FROM msg_id').fetchone())
		msg1  = msg1 .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		winner = str(con.execute(f'SELECT winners FROM draw').fetchone())
		winner  = winner .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		prize = str(con.execute(f'SELECT prize FROM draw WHERE id = {int(ing)}').fetchone())
		prize  = prize.replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		text = str(con.execute(f'SELECT text FROM draw WHERE id = {int(ing)}').fetchone())
		text  = text .replace('(', '').replace(')', '').replace(',', '').replace("'", '')
		cur.execute("select * from users")
		results = cur.fetchall()
		await call.bot.edit_message_caption(caption=f"❗Внимание Розыгрыш!\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n🎁Приз: {prize}\n📢{text}\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nКолличество участников: {len(results)}\nПобедитель: 👑{winner}",chat_id=int(config['settings']['channel_id']), message_id=int(msg1), reply_markup=close)
		history = (prize, text, winner, (len(results)))
		cur.execute('INSERT INTO history ("prize", "text", "winners", "number") VALUES(?, ?, ?, ?)', history) 
		con.commit()
		con.execute(f"DELETE FROM msg_id")
		con.execute(f"DELETE FROM users")
		con.execute(f"DELETE FROM draw")
		con.commit()
		
	
async def main():
	await dp.start_polling(bot)
if __name__ == "__main__":
	asyncio.run(main())