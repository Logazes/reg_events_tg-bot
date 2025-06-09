from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
from  pytz import timezone
from sqlalchemy import and_
from __init__ import bot
from utils import is_admin
from database import Session
from models import User, Event, Registration

def start(message):
    with Session() as db:
        bot.send_message(message.chat.id,"Привет")
        if db.query(User).filter(User.tg_id == message.chat.id).first():
            bot.send_message(message.chat.id,"вы уже зарегистрированы")
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("Профиль"))
            markup.add(KeyboardButton("Актуальные события"))
            if is_admin(message, db):
                markup.add(KeyboardButton("Создать событие"))
                markup.add(KeyboardButton("Повысить пользователя до администратора"))
            bot.send_message(message.chat.id, text="Привет", reply_markup=markup)
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
    show_info(message)

def show_info(message):
    with Session() as db:
        query = (
            db
            .query(Registration, Event, User)
            .select_from(Registration)
            .join(
                Event,
                Registration.event == Event.id,
                isouter=True)
            .join(
                User,
                Registration.user == User.tg_id
            )
            .filter(
                User.tg_id == message.chat.id
            )
        )
        user = query[0][2]
        text = f"""
        {user.last_name} {user.first_name[0]}. {user.middle_name[0]}.\n
    Группа: {user.group}\n
    События на которые вы записаны:
    {"\n".join([f"{event.title} {event.start_time}" for _, event, _ in query])}
        """
    bot.send_message(message.chat.id, text)

def show_active_events(message):
    with Session() as db:
        events = list(db.query(Event).filter(Event.start_time >= datetime.now(timezone('Europe/Moscow'))))
        if len(events) == 0:
            bot.send_message(message.chat.id, "На данный момент нет активных событий")
        else:
            for event in events:
                markup = InlineKeyboardMarkup()
                if db.query(User).filter(User.tg_id == message.chat.id).first().admin:
                    markup.add(InlineKeyboardButton("Показать участников", callback_data=f"display_{message.chat.id}_{event.id}"))
                    markup.add(InlineKeyboardButton("Экспорт участников", callback_data=f"export_{message.chat.id}_{event.id}"))
                markup.add(InlineKeyboardButton("Принять участие", callback_data=f"event_{message.chat.id}_{event.id}"))
                bot.send_message(message.chat.id, f"Тип: {event.type}\nНазвание: {event.title}\nДата и время проведения: {event.start_time}", reply_markup=markup)