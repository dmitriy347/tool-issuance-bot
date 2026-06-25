from os import getenv
import pytest
from dotenv import load_dotenv
from sqlalchemy import URL
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Загружаем .env сразу при импорте conftest.py, ДО того, как соберём TEST_DATABASE_URL.
# Здесь это нормально, т.к. conftest.py существует только для тестов.
load_dotenv()

@pytest.fixture(autouse=True)
def setup_env():
    """Загружает переменные окружения из .env перед выполнением каждого теста."""
    load_dotenv()

# Собираем URL тестовой БД.
# Используем те же DB_USER/DB_PASSWORD/DB_HOST/DB_PORT, что и в database.py, но другое имя базы — TEST_DB_NAME.
TEST_DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=getenv("DB_USER"),
    password=getenv("DB_PASSWORD"),
    host=getenv("TEST_DB_HOST"),
    port=getenv("DB_PORT"),
    database=getenv("TEST_DB_NAME"),
)
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest.fixture
async def db_session():
    """
    Создаёт чистые таблицы перед тестом, отдаёт сессию тесту, после теста удаляет таблицы.
    """
    from database import Base
    from models.employee import Employee
    from models.inventory import Inventory

    # .begin() открывает транзакцию и сам делает коммит при выходе из блока.
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        # Отдаём сессию каждому тесту через yield.
        yield session

    # После теста удаляем все таблицы.
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)