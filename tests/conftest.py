import pytest
from dotenv import load_dotenv

@pytest.fixture(autouse=True)
def setup_env():
    """Загружает переменные окружения из .env перед выполнением каждого теста."""
    load_dotenv()