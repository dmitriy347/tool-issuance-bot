import pytest
from pydantic import ValidationError

from api.schemas.ai_extraction import ExtractedNames


def test_extracted_names_valid_cyrillic():
    """Корректные фамилии на кириллице проходят валидацию."""
    names = ExtractedNames(primary="Иванов", second="Петров", third=None)
    assert names.primary == "Иванов"
    assert names.second
    assert names.third is None


def test_extracted_names_invalid_cyrillic():
    """Фамилия на латинице вызывают ошибку валидации."""
    with pytest.raises(ValidationError):
        ExtractedNames(primary="Ivanov")


def test_extracted_names_mixed_alphabet():
    """Фамилия со смешанным алфавитом вызывают ошибку валидации."""
    with pytest.raises(ValidationError):
        ExtractedNames(primary="Иванov")