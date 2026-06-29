from pathlib import Path

from services.ai_extractor import extract_employee_names


async def test_extract_single_employee_names():
    """
    Тестирование функции extract_employee_names на корректность извлечения фамилии сотрудника из изображения.
    Один сотрудник.
    """
    image_bytes = (Path(__file__).parent / "fixtures" / "screen_1_person.png").read_bytes()
    result = await extract_employee_names(image_bytes)

    assert result.second is None
    assert result.third is None
    assert len(result.primary.split()) == 1
    assert "Пономарев" in result.primary


async def test_extract_two_employee_names():
    """
    Тестирование функции extract_employee_names на корректность извлечения фамилий сотрудников из изображения.
    Два сотрудника.
    """
    image_bytes = (Path(__file__).parent / "fixtures" / "screen_2_person.png").read_bytes()
    result = await extract_employee_names(image_bytes)

    assert result.third is None
    assert result.second is not None
    assert len(result.primary.split()) == 1
    assert len(result.second.split()) == 1
    assert "Морозенко" in result.primary
    assert "Эйдельман" in result.second

async def test_extract_three_employee_names():
    """
    Тестирование функции extract_employee_names на корректность извлечения фамилий сотрудников из изображения.
    Три сотрудника.
    """
    image_bytes = (Path(__file__).parent / "fixtures" / "screen_3_person.png").read_bytes()
    result = await extract_employee_names(image_bytes)

    assert result.second is not None
    assert result.third is not None
    assert len(result.primary.split()) == 1
    assert len(result.second.split()) == 1
    assert len(result.third.split()) == 1
    assert "Батурин" in result.primary
    assert "Белозеров" in result.second
    assert "Шароваров" in result.third
