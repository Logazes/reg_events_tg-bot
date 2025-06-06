import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from datetime import datetime
from  pytz import timezone
from database import Session
from models import User, Event, Registration
from utils import export_registered_users
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
    show_info(message)

@bot.message_handler(commands=['info'])
def show_info(message):
    with Session() as db:
        user = db.query(User).filter(User.tg_id == message.chat.id).first()
    bot.send_message(message.chat.id, f"Вас зовут: {user.last_name} {user.first_name[0]}. {user.middle_name[0]}.\nГруппа: {user.group}")

@bot.message_handler(commands=["active_events"])
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

@bot.message_handler(commands=["create_event"])
def create_event(message):
    with Session() as db:
        if db.query(User).filter(User.tg_id == message.chat.id).first.admin:
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

@bot.message_handler(commands=["create_admin"])
def create_admin(message):
    with Session() as db:
        if db.query(User).filter(User.tg_id == message.chat.id).first.admin:
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

@bot.message_handler(commands=['menu'])
def menu(message):
    pass

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = str(call.data).split('_')
    if data[0] == 'event':
        with Session() as db:
            if not db.query(Registration).filter((Registration.user == data[1]) & (Registration.event == data[2])).first():
                db.add(Registration(user=data[1], event= data[2]))
                db.commit()
                bot.answer_callback_query(call.id, "Вы записаны на событие")
            else:
                bot.answer_callback_query(call.id, f"Вы уже записаны на событие")
    elif data[0] == "display":
        with Session() as db:
            users_ids = [i.user for i in db.query(Registration).filter(Registration.event == int(data[2]))]
            users = list()
            for id in users_ids:
                user = db.query(User).filter(User.tg_id == id).first()
                users.append(f"{user.last_name} {user.first_name[0]}. {user.middle_name[0]}. {user.group}")
            bot.send_message(data[1], '\n'.join(users))
    elif data[0] == "export":
        file = export_registered_users(data[2])
        with open(file, 'rb') as f:
            bot.send_document(
                data[1],
                InputFile(f, file_name= file)
                
            )
            
            

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.infinity_polling()