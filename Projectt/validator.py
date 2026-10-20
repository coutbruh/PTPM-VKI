# validators.py
import re
import hashlib
import logging

BLACKLIST = {
    "admin", "root", "user", "test", "guest",
    "qwerty", "12345", "moderator", "support",
}
MIN_LOGIN_LEN = 5
MIN_PASSWORD_LEN = 7

PHONE_RE = re.compile(r"\+\d-\d{3}-\d{3}-\d{4}")
EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")
PLAIN_RE = re.compile(r"[A-Za-z0-9_]{5,}")

CYR_UPPER_RE = re.compile(r"[А-ЯЁ]")
CYR_LOWER_RE = re.compile(r"[а-яё]")
DIGIT_RE = re.compile(r"\d")
SPECIAL_RE = re.compile(r"[^\w\s]")
LATIN_RE = re.compile(r"[A-Za-z]")


def mask_password(password: str) -> str:
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return "***" + digest[:8]


class Validator:
    """Класс валидации регистрационных данных (требование п. a)."""

    def validate_registration(self, login: str, password: str, confirm: str) -> tuple[bool, str]:
        logging.debug(
            "Валидация: login=%s, pwd=%s, confirm=%s",
            login, mask_password(password), mask_password(confirm),
        )

        ok, msg = self._validate_login(login)
        if not ok:
            logging.error("Ошибка валидации логина: %s", msg)
            return False, msg

        ok, msg = self._validate_password(password)
        if not ok:
            logging.error("Ошибка валидации пароля: %s", msg)
            return False, msg

        if password != confirm:
            logging.error("Пароли не совпадают")
            return False, "Пароли не совпадают"

        logging.info("Регистрация успешна: login=%s", login)
        return True, ""

    # ---------- приватные проверки ----------

    def _validate_login(self, login: str) -> tuple[bool, str]:
        if not login:
            return False, "Логин пустой"
        if login.lower() in BLACKLIST:
            return False, "Логин находится в чёрном списке"
        if PHONE_RE.fullmatch(login):
            return True, ""
        if EMAIL_RE.fullmatch(login):
            return True, ""
        if PLAIN_RE.fullmatch(login):
            return True, ""

        if len(login) < MIN_LOGIN_LEN and "@" not in login and not login.startswith("+"):
            return False, f"Логин короче {MIN_LOGIN_LEN} символов"
        if "@" in login:
            return False, "Неверный формат email"
        if login.startswith("+"):
            return False, "Неверный формат телефона (ожидается +x-xxx-xxx-xxxx)"
        if LATIN_RE.search(login) or DIGIT_RE.search(login) or "_" in login:
            return False, "Логин содержит недопустимые символы"
        return False, "Логин не соответствует ни одному допустимому формату"

    def _validate_password(self, password: str) -> tuple[bool, str]:
        if not password:
            return False, "Пароль пустой"
        if len(password) < MIN_PASSWORD_LEN:
            return False, f"Пароль короче {MIN_PASSWORD_LEN} символов"
        if LATIN_RE.search(password):
            return False, "Пароль содержит латинские буквы (разрешена только кириллица)"
        if not CYR_UPPER_RE.search(password):
            return False, "Пароль не содержит заглавной кириллической буквы"
        if not CYR_LOWER_RE.search(password):
            return False, "Пароль не содержит строчной кириллической буквы"
        if not DIGIT_RE.search(password):
            return False, "Пароль не содержит цифры"
        if not SPECIAL_RE.search(password):
            return False, "Пароль не содержит специального символа"
        return True, ""