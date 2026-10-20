# notifier.py
import logging
from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    """Интерфейс отправки данных стороннему процессу (требование п. d)."""

    @abstractmethod
    def send(self, message: str) -> bool:
        ...


class FakeEmailNotifier(BaseNotifier):
    """Имитация отправки на email-сервер (реальной сети нет)."""

    def __init__(self):
        self.sent: list[str] = []

    def send(self, message: str) -> bool:
        logging.info("Имитация отправки на email-сервер: %s", message)
        self.sent.append(message)
        return True