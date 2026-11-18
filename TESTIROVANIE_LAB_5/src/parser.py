"""Модуль 2: Веб-парсер ForumParser."""
from dataclasses import dataclass, asdict
from typing import Iterable
import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}
  

@dataclass
class ParsedComment:
    id: int
    name: str
    message: str


class ForumParser:
    """Парсер постов форума."""

    def __init__(self, headers: dict | None = None, timeout: int = 10) -> None:
        self.headers = headers or DEFAULT_HEADERS
        self.timeout = timeout

    # ---------- загрузка ----------
    def _fetch(self, url: str) -> str:
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    # ---------- разбор ----------
    def parse_html(self, html: str) -> list[ParsedComment]:
        """Разбирает HTML-строку и возвращает список постов."""
        soup = BeautifulSoup(html, "lxml")
        posts: list[ParsedComment] = []

        for node in soup.select("[data-comment-id]"):
            raw_id = node.get("data-comment-id")
            if raw_id is None:
                continue
            try:
                comment_id = int(raw_id)
            except (TypeError, ValueError):
                continue

            name_node = node.select_one(".username")
            message_node = node.select_one(".message")

            name = name_node.get_text(strip=True) if name_node else ""
            # Внутренняя HTML-разметка сообщения сохраняется через decode_contents
            message = (
                message_node.decode_contents().strip()
                if message_node
                else ""
            )

            if not name or not message:
                continue

            posts.append(ParsedComment(id=comment_id, name=name, message=message))

        return posts

    def parse_page(self, url: str) -> list[ParsedComment]:
        """Скачивает страницу и возвращает разобранные посты."""
        html = self._fetch(url)
        return self.parse_html(html)

    # ---------- сохранение в БД ----------
    def save_to_db(self, parsed_data: Iterable[ParsedComment], repository) -> int:
        """Сохраняет посты через DatabaseRepository. Возвращает число вставок."""
        saved = 0
        for item in parsed_data:
            try:
                repository.add(item.id, item.name, item.message)
                saved += 1
            except Exception:
                # пропускаем дубликаты / некорректные записи
                continue
        return saved