# tests/test_integration.py
import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, r"C:\Users\KL\Desktop\Projectt") 

from controller import Controller
from database import RegistrationDB
from notifier import BaseNotifier
from user_io import BaseUserIO
from validator import Validator


def make_controller(login, password, confirm):
    """Хелпер: собирает контроллер с реальными Validator+DB и моками границ."""
    db = RegistrationDB(":memory:")

    io = MagicMock(spec=BaseUserIO)
    io.get_registration_data.return_value = (login, password, confirm)

    notifier = MagicMock(spec=BaseNotifier)
    notifier.send.return_value = True

    ctrl = Controller(io, db, notifier, Validator())
    return ctrl, db, notifier


class TestRegistrationIntegration(unittest.TestCase):
    """Интеграционные тесты сквозного сценария регистрации."""

    def test_valid_data_full_flow(self):
        """Валидные данные True, запись в БД, отправка нотификации."""
        ctrl, db, notifier = make_controller("my_login", "Пароль1!", "Пароль1!")

        ok, msg = ctrl.run_registration()

        self.assertTrue(ok)
        self.assertEqual(msg, "")
        # запись сохранена в БД
        self.assertEqual(
            db.get("my_login", "Пароль1!", "Пароль1!"), (True, "")
        )
        # внешняя зависимость вызвана ровно один раз
        notifier.send.assert_called_once()
        db.close()

    def test_invalid_password_full_flow(self):
        """Невалидный пароль → False, запись в БД сохранена с ошибкой, нотификация была."""
        ctrl, db, notifier = make_controller("my_login", "short", "short")

        ok, msg = ctrl.run_registration()

        self.assertFalse(ok)
        self.assertIn("короче", msg.lower())
        cached = db.get("my_login", "short", "short")
        self.assertIsNotNone(cached)
        self.assertFalse(cached[0])
        notifier.send.assert_called_once()
        db.close()

    def test_repeated_request_hits_cache(self):
        """Повторный вызов с теми же данными валидатор не вызывается повторно."""
        db = RegistrationDB(":memory:")
        io = MagicMock(spec=BaseUserIO)
        io.get_registration_data.return_value = ("my_login", "Пароль1!", "Пароль1!")
        notifier = MagicMock(spec=BaseNotifier)

        validator = MagicMock(wraps=Validator())  # реальный, но считаем вызовы
        validator.validate_registration = MagicMock(
            side_effect=Validator().validate_registration
        )

        ctrl = Controller(io, db, notifier, validator)
        ctrl.run_registration()
        ctrl.run_registration()

        # валидатор вызван только в первый раз
        self.assertEqual(validator.validate_registration.call_count, 1)
        # нотификация вызвана оба раза
        self.assertEqual(notifier.send.call_count, 2)
        db.close()

    def test_passwords_mismatch_full_flow(self):
        """Пароли не совпадают False, ошибка «Пароли не совпадают»."""
        ctrl, db, notifier = make_controller("my_login", "Пароль1!", "Другой2@")

        ok, msg = ctrl.run_registration()

        self.assertFalse(ok)
        self.assertEqual(msg, "Пароли не совпадают")
        notifier.send.assert_called_once()
        db.close()


if __name__ == "__main__":
    unittest.main()