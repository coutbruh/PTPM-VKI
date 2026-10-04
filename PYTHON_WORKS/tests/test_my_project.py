import unittest
import sys
import os

from src.validator import (
    validate_login,
    validate_password,
    validate_registration,
    mask_password,
)
class SimpleUnitTest(unittest.TestCase):
    def test_LoginEmptyUnitTest(self):
        ok,msg=validate_login("")
        self.assertFalse(ok)
        self.assertEqual(msg,"Логин пустой")
    def test_LoginBlacklistUnitTest(self):
        ok,msg=validate_login("admin")
        self.assertFalse(ok)
        self.assertEqual(msg,"Логин находится в чёрном списке")
    def test_LoginUncorrect(self):
        ok, msg = validate_login("user@")     
        self.assertFalse(ok)
        self.assertEqual(msg, "Неверный формат email")
    def test_phoneFormat_TrueUnitTest(self):
        ok,msg=validate_login("+7-985-912-2341")
        self.assertTrue(ok,msg)
    def test_EmailFormat_TrueUnitTest(self):
        ok,msg=validate_login("hexdohg@gmail.com")
        self.assertTrue(ok,msg)


    def test_passwordMaskUnitTest(self):
        res=mask_password("drfgeeeeeefgbdxcb")
        self.assertTrue(res.startswith("***"))
        self.assertEqual(len(res), 11)
    def test_passwordEmptyUnitTest(self):
        ok,msg=validate_password("")
        self.assertFalse(ok)
        self.assertEqual(msg,"Пустой пароль")
    def test_UncorrectLenPassUnitTest(self):
        ok,msg=validate_password("123")
        self.assertFalse(ok)
        self.assertEqual(msg,"Слишком короткий пароль")
    def test_PassNotConsistNumUnitTest(self):
        ok,msg=validate_password("Пароль!!")
        self.assertFalse(ok)
        self.assertEqual(msg,"Нет цифр")
    def test_PassWithoutSpecSymbUnitTest(self):
        ok,msg=validate_password("Пароль11")
        self.assertFalse(ok)
        self.assertEqual(msg, "Нет спецсимволов")
