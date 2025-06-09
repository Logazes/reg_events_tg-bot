import pandas as pd
from models import Registration, User, Event
from database import Session

def is_admin(message, db):
    return db.query(User).filter(User.tg_id == message.chat.id).first().admin

def export_registered_users(event_id):
    with Session() as db:
        users_ids = [i.user for i in db.query(Registration).filter(Registration.event == event_id)]
        data = {"Фамилия": [],
                "Имя": [],
                "Отчество": [],
                "Группа": []}
        for id in users_ids:
            user = db.query(User).filter(User.tg_id == id).first()
            data["Фамилия"].append(user.last_name)
            data["Имя"].append(user.first_name)
            data["Отчество"].append(user.middle_name)
            data["Группа"].append(user.group)

        data = pd.DataFrame(data)
        event_title = str(db.query(Event).filter(Event.id == event_id).first().title).replace(" ", "_")
        file = f"./export/{event_title}.xlsx"
        data.to_excel(file)
        return file
