from sqlalchemy import  Column, Integer, String, Boolean, DateTime
from database import Base, engine
from datetime import datetime
from  pytz import timezone

class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)

class User(BaseModel):
    __tablename__ = "users"

    tg_id = Column(Integer) # телеграмм ID
    first_name = Column(String) # имя
    middle_name = Column(String) # отчество
    last_name = Column(String) # фамилия
    group = Column(String) # группа
    admin = Column(Boolean, default=False) # является ли админом

class Event(BaseModel):
    __tablename__ = "events"

    type = Column(String) # тип события
    creator = Column(Integer) # телеграмм ID автора
    title = Column(String) # название
    created_timestamp = Column(DateTime, default=datetime.now(timezone('Europe/Moscow'))) # время создания события
    start_time = Column(DateTime) # время начала события

class Registration(BaseModel):
    __tablename__ = "registrations"

    user = Column(Integer) # телеграмм ID пользователя
    event = Column(Integer) # ID события

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)