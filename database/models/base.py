from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connection MySQL sur port 3307
DATABASE_URL = "mysql+mysqlconnector://root@localhost:3307/smartautorisk"

engine = create_engine(DATABASE_URL, echo=True)  # echo=True pour debug SQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    return SessionLocal()

Base = declarative_base()