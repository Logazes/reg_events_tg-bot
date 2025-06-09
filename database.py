from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# строка подключения
sqlite_database = "sqlite:///metanit.db"
# создаем движок SqlAlchemy
engine = create_engine(sqlite_database, echo=False)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# создаем модель, объекты которой будут храниться в бд
class Base(DeclarativeBase): pass