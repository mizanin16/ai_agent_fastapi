from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/test-response-size")
async def test_response_size(size: int = Query(..., ge=1, le=500000)):
    """
    Возвращает JSON-объект с полем `payload`, содержащим строку заданной длины.
    Используется для тестирования ограничений на размер ответа.
    """
    content = generate_random_russian_text(size)
    return JSONResponse(content={"length": len(content), "payload": content})


import random

# Расширенный список русских слов (можно дополнить)
RUSSIAN_WORDS = [
    "данные", "анализ", "тест", "вход", "выход", "модель", "функция", "ошибка", "код",
    "система", "объект", "метод", "класс", "массив", "база", "память", "поток",
    "логика", "агент", "ответ", "вопрос", "запрос", "документ", "ключ", "параметр",
    "результат", "структура", "файл", "текст", "строка", "длина", "цикл", "программа",
    "библиотека", "сервер", "интерфейс", "импорт", "обработка", "исходник", "лог",
    "статус", "объём", "порог", "коллекция", "транскрипт", "сравнение", "фреймворк"
]


def generate_random_russian_text(char_count: int) -> str:
    if char_count <= 0:
        return ""

    result = []
    while sum(len(w) for w in result) + len(result) - 1 < char_count:
        result.append(random.choice(RUSSIAN_WORDS))

    text = " ".join(result)
    return text[:char_count]
