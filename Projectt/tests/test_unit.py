# tests/test_unit.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, r"C:\Users\KL\Desktop\Projectt") 
from database import RegistrationDB
from notifier import FakeEmailNotifier, BaseNotifier
from user_io import ConsoleUserIO
from controller import Controller
from validator import Validator


class TestRegistrationDB(unittest.TestCase):
    """Юнит-тесты класса БД: add / get / delete."""

    def setUp(self):
        self.db = RegistrationDB(":memory:")

    def tearDown(self):
        self.db.close()

    def test_add_and_get(self):
        self.db.add("user_login", "Пароль1!", "Пароль1!", True, "")
        self.assertEqual(
            self.db.get("user_login", "Пароль1!", "Пароль1!"),
            (True, ""),
        )

    def test_get_missing_returns_none(self):
        self.assertIsNone(self.db.get("nobody", "x", "x"))

    def test_delete(self):
        self.db.add("user_login", "Пароль1!", "Пароль1!", True, "")
        self.assertTrue(self.db.delete("user_login", "Пароль1!", "Пароль1!"))
        self.assertIsNone(self.db.get("user_login", "Пароль1!", "Пароль1!"))
        # повторное удаление возвращает False
        self.assertFalse(self.db.delete("user_login", "Пароль1!", "Пароль1!"))


class TestConsoleUserIO(unittest.TestCase):
    """Юнит-тест класса IO с замоканным input()."""

    @patch("builtins.input", side_effect=["my_login", "Пароль1!", "Пароль1!"])
    def test_get_registration_data(self, _mock_input):
        io = ConsoleUserIO()
        self.assertEqual(
            io.get_registration_data(),
            ("my_login", "Пароль1!", "Пароль1!"),
        )


class TestFakeNotifier(unittest.TestCase):
    """Юнит-тест notifier: вызов send сохраняет сообщение."""

    def test_send_stores_message(self):
        n = FakeEmailNotifier()
        self.assertTrue(n.send("hello"))
        self.assertEqual(n.sent, ["hello"])


class TestControllerUsesCache(unittest.TestCase):
    """
    Юнит-тест контроллера: при повторном запросе валидатор НЕ вызывается,
    результат берётся из БД.
    """

    def test_second_call_uses_db_not_validator(self):
        db = RegistrationDB(":memory:")
        validator = MagicMock(spec=Validator)
        validator.validate_registration.return_value = (True, "")
        io = MagicMock()
        io.get_registration_data.return_value = ("my_login", "Пароль1!", "Пароль1!")
        notifier = MagicMock(spec=BaseNotifier)

        ctrl = Controller(io, db, notifier, validator)

        # 1-й вызов — валидатор сработал, запись создана
        ctrl.run_registration()
        self.assertEqual(validator.validate_registration.call_count, 1)

        # 2-й вызов — данные уже в БД валидатор НЕ должен вызываться
        ctrl.run_registration()
        self.assertEqual(validator.validate_registration.call_count, 1)

        db.close()


if __name__ == "__main__":
    unittest.main()