import base64
import json
import httpx
from os import getenv

from api.schemas.ai_extraction import ExtractedNames

text = ("Проанализируй файл, найди и прочитай поле Комментарий, проверь его на наличие символа \"/\","
        "в зависимости от количества этих символов выбери один из 3 вариантов развития событий:"
        "если в поле Комментарий НЕТ символа \"/\" - значит это 1 вариант - взять ТОЛЬКО первое слово целиком как last_name_1, last_name_2 == null, last_name_3 == null, ВСЕ последующие слова игнорировать,"
        "если в поле Комментарий есть ТОЛЬКО 1 символ \"/\" - значит это 2 вариант - взять последнее слово перед символом \"/\" как last_name_1, и первое слово после символа \"/\" как last_name_2, last_name_3 == null,"
        "если в поле Комментарий есть 2 символа \"/\" - значит это 3 вариант - взять последнее слово перед первым символом \"/\" как last_name_1, взять последнее слово перед вторым символом \"/\" как last_name_2, и первое слово после второго символа \"/\" как last_name_3,"
        "Когда определишь подходящий из этих трех вариантов - верни ТОЛЬКО JSON, без пояснений и markdown-форматирования в формате {\"primary\": last_name_1, \"second\": last_name_2, \"third\": last_name_3}")

url = "https://api.groq.com/openai/v1/chat/completions"
model = "qwen/qwen3.6-27b"

async def extract_employee_names(image_bytes: bytes) -> ExtractedNames:
    """
    Отправляет изображение и текстовый запрос в модель для извлечения фамилии сотрудника из поля "Комментарий".
    response_format указывает, что мы ожидаем получить JSON-объект в ответе.
    reasoning_effort отключает thinking mode.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {getenv('GROQ_API_KEY')}"
    }
    body = {
        "model": model,
        "response_format": {"type": "json_object"},
        "temperature": 0,
        "reasoning_effort": "none",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            # Изображение передается не как файл, а как base64-строка
                            "url": "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode('utf-8')
                        }
                    },
                    {
                        "type": "text",
                        # Промпт
                        "text": text
                    }
                ]
            }
        ]
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(45.0)) as client:
        # Отправляем POST-запрос к API Groq с изображением и промтом, получаем JSON-ответ
        response = await client.post(url, headers=headers, json=body)
        response.raise_for_status()
        # Извлекаем текстовый ответ модели, который должен быть JSON-строкой
        data = response.json()["choices"][0]["message"]["content"]

        # Распарсим строку JSON в словарь Python
        result = json.loads(data)
        return ExtractedNames.model_validate(result)