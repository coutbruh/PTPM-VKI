# user_io.py
from abc import ABC, abstractmethod


class BaseUserIO(ABC):
    """Интерфейс взаимодействия с пользователем (требование п. c)."""

    @abstractmethod
    def get_registration_data(self) -> tuple[str, str, str]:
        """Возвращает (login, password, confirm)."""
        ...

    @abstractmethod
    def show_result(self, ok: bool, message: str) -> None:
        ...


class ConsoleUserIO(BaseUserIO):
    """Консольная реализация через input()/print()."""

    def get_registration_data(self) -> tuple[str, str, str]:
        login = input("Введите логин: ").strip()
        password = input("Введите пароль: ")
        confirm = input("Подтвердите пароль: ")
        return login, password, confirm

    def show_result(self, ok: bool, message: str) -> None:
        print("True" if ok else "False")
        print(message)