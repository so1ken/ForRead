# Сущность Книги с ее полями 
from dataclasses import dataclass # Генератор шаблонного кода
from typing import Optional # Инструмент для аннотации типов

@dataclass
class Book:
    id: Optional[int] = None  # ID будет None, пока мы не сохраним книгу в БД
    title: str = ""
    author: str = ""
    pages_total: int = 0
    pages_read: int = 0
    review: str = ""
    cover_path: str = ""
    