from os import getenv

from sqlalchemy import create_engine, URL
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = URL.create(
    drivername="postgresql",
    username=getenv("DB_USER"),
    password=getenv("DB_PASSWORD"),
    host=getenv("DB_HOST"),
    port=getenv("DB_PORT"),
    database=getenv("DB_NAME"),
)

engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass
