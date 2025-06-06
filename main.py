from telebot.types import InputFile
from database import Session
from models import User, Event, Registration
from utils import export_registered_users
import user, admin
from __init__ import bot

@bot.message_handler(commands=['start', 'help'])
def start(message):
    user.start(message)

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
                bot.answer_callback_query(call.id, "Вы уже записаны на событие")
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
            
@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == "Профиль":
        user.show_info(message)
    elif message.text == "Меню":
        pass
    elif message.text == "Актуальные события":
        user.show_active_events(message)
    elif message.text == "Создать событие":
        admin.create_event(message)
    elif message.text == "Повысить пользователя до администратора":
        admin.create_admin(message)

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.infinity_polling()