import telebot
from telebot import types
from database import Session
from models import User, Event
from keys import tg_token as token
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    with Session() as db:
        bot.send_message(message.chat.id,"Привет")
        if db.query(User).filter(User.tg_id == message.chat.id).first():
            bot.send_message(message.chat.id,"вы уже зарегистрированы")
        else: 
            bot.send_message(message.chat.id, "пока что вы не зарегистрированы")
            bot.send_message(message.chat.id, "Чтобы пройти регистрацию напишите свою фамилию")
            bot.register_next_step_handler(message, add_last_name)

def add_last_name(message):
    with Session() as db:
        db.add(User(tg_id=message.chat.id, last_name=message.text.replace(' ', '')))
        db.commit()
    bot.send_message(message.chat.id, "теперь имя")
    bot.register_next_step_handler(message, add_first_name)

def add_first_name(message):
    with Session() as db:
        db.query(User).filter(User.tg_id == message.chat.id).first().first_name = message.text.replace(' ', '')
        db.commit()
    bot.send_message(message.chat.id, "отчество")
    bot.register_next_step_handler(message, add_middle_name)

def add_middle_name(message):
    with Session() as db:
        db.query(User).filter(User.tg_id == message.chat.id).first().middle_name = message.text.replace(' ', '')
        db.commit()
    bot.send_message(message.chat.id, "осталось ввести группу")
    bot.register_next_step_handler(message, add_group)

def add_group(message):
    with Session() as db:
        db.query(User).filter(User.tg_id == message.chat.id).first().group = message.text.replace(' ', '')
        db.commit()
    bot.send_message(message.chat.id, "вы зарегистрированы")

@bot.message_handler(commands=['info'])
def show_info(message):
    with Session() as db:
        user = db.query(User).filter(User.tg_id == message.chat.id).first()
    bot.send_message(message.chat.id, f"Вас зовут: {user.last_name} {user.first_name[0]}. {user.middle_name[0]}.\nГруппа: {user.group}")

@bot.message_handler(commands=['menu'])
def menu(message):
    pass

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.infinity_polling()