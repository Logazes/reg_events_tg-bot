import telebot
from telebot import types
from database import Session
from models import User, Event
token = '7617704331:AAG0-vPN4S3bxawZH8T6jgP28Lw0mEUy8-I'
bot = telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start(message):
    with Session() as db:
        bot.send_message(message.chat.id,"Привет")
        bot.send_message(message.chat.id,f"Ваш id: {message.chat.id}")
        if db.query(User).filter(User.tg_id == message.chat.id).first():
            bot.send_message(message.chat.id,"вы уже зарегистрированы")
        else: 
            bot.send_message(message.chat.id, "пока что вы не зарегистрированы")
            bot.send_message(message.chat.id, "Чтобы пройти регистрацию напишите свои имя, фамилию, отчество и группу")
        
@bot.message_handler(commands=['menu'])
def menu(message):
    pass
bot.infinity_polling()