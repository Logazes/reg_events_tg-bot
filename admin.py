from datetime import datetime
from database import Session
from models import User, Event, Registration
from __init__ import bot

def create_event(message):
    with Session() as db:
        if db.query(User).filter(User.tg_id == message.chat.id).first().admin:
            bot.send_message(message.chat.id, "Введите название события")
            bot.register_next_step_handler(message, add_title)
        else: 
            bot.send_message(message.chat.id, "Эта функция доступна только администраторам")

def add_title(message):
    with Session() as db:
        db.add(Event(title=message.text, creator= message.chat.id, type= "спорт"))
        db.commit()
    bot.send_message(message.chat.id, "Введите дату и время в формате ГГГГ-ММ-ДД ЧЧ:ММ:СС")
    bot.register_next_step_handler(message, add_date)

def add_date(message):
    with Session() as db:
        db.query(Event).filter((Event.creator == message.chat.id) & (Event.start_time == None)).first().start_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M:%S")
        db.commit()
        bot.send_message(message.chat.id, "Событие добавлено")

def create_admin(message):
    with Session() as db:
        if db.query(User).filter(User.tg_id == message.chat.id).first().admin:
            bot.send_message(message.chat.id, "Введите телеграмм ID пользователя")
            bot.register_next_step_handler(message, add_admin_id)
        else: 
            bot.send_message(message.chat.id, "Эта функция доступна только администраторам")

def add_admin_id(message):
    with Session() as db:
        tg_id = int(message.text)
        print(tg_id)
        db.query(User).filter(User.tg_id == tg_id).first().admin = True
        db.commit()
    bot.send_message(message.chat.id, "Пользователь повышен до администратора")