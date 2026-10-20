# controller.py
import logging

from database import RegistrationDB
from user_io import BaseUserIO
from notifier import BaseNotifier
from validator import Validator


class Controller:
    """Контроллер бизнес-логики (требование п. e)."""

    def __init__(self, user_io: BaseUserIO, db: RegistrationDB,
                 notifier: BaseNotifier, validator: Validator):
        self.user_io = user_io
        self.db = db
        self.notifier = notifier
        self.validator = validator

    def run_registration(self) -> tuple[bool, str]:
        login, password, confirm = self.user_io.get_registration_data()

        cached = self.db.get(login, password, confirm)
        if cached is not None:
            ok, msg = cached
            logging.info("Результат взят из БД для login=%s", login)
        else:
            ok, msg = self.validator.validate_registration(login, password, confirm)
            self.db.add(login, password, confirm, ok, msg)
            logging.info("Результат вычислен и сохранён в БД для login=%s", login)

        self.notifier.send(f"login={login}; result={ok}; msg={msg}")
        self.user_io.show_result(ok, msg)
        return ok, msg