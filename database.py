from os import getenv

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=getenv("DB_USER"),
    password=getenv("DB_PASSWORD"),
    host=getenv("DB_HOST"),
    port=getenv("DB_PORT"),
    database=getenv("DB_NAME"),
)

# 1. Engine — соединение с БД
engine = create_async_engine(DATABASE_URL)

# 2. Сессии
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# 3. Dependency для роутеров
async def get_db() -> AsyncSession:
    """Dependency для роутеров. Создаёт сессию БД на время запроса и закрывает после."""
    async with AsyncSessionLocal() as session:
        yield session  # именно yield, а не return - FastAPI автоматически закроет сессию сам


class Base(DeclarativeBase):
    pass
