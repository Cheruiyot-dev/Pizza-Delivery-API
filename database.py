from dotenv import load_dotenv
import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = get_db()


def create_tables():
    import models
    Base.metadata.create_all(bind=engine)


def check_and_create_tables():
    inspector = inspect(engine)
    if not inspector.get_table_names():
        create_tables()
        print("Tables created successfully")
    else:
        print("Tables already exist.")


check_and_create_tables()
