import base64
import json
import httpx
from os import getenv

from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, retry_if_exception_type

from api.schemas.ai_extraction import ExtractedNames

text = (
    "Найди поле «Комментарий» на изображении и определи фамилии сотрудников по следующим правилам:\n"
    "Все фамилии пиши только кириллицей (русский алфавит), без латинских букв, даже если отдельные буквы похожи.\n"
    "- Если в поле нет символа \"/\": primary = первое слово, second = null, third = null.\n"
    "- Если есть один символ \"/\": primary = последнее слово перед \"/\", second = первое слово после \"/\", third = null.\n"
    "- Если есть два символа \"/\": primary = последнее слово перед первым \"/\", second = последнее слово перед вторым \"/\", third = первое слово после второго \"/\".\n"
    "Верни ТОЛЬКО JSON без пояснений и markdown-форматирования: "
    "{\"primary\": фамилия, \"second\": фамилия или null, \"third\": фамилия или null}"
)

url = "https://api.groq.com/openai/v1/chat/completions"
model = "qwen/qwen3.6-27b"


@retry(
    stop=stop_after_attempt(2),
    retry=retry_if_exception_type((ValidationError, json.JSONDecodeError)),
    reraise=True,
)
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