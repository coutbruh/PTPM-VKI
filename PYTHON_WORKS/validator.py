import re
import hashlib
import logging

BLACKLIST = {
    "admin", "root", "user", "test", "guest",
    "qwerty", "12345", "moderator", "support"
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

# ---------- Валидация логина ----------

def validate_login(login: str) -> tuple[bool, str]:
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


# ---------- Валидация пароля ----------

def validate_password(password: str) -> tuple[bool, str]:

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



def validate_registration(
    login: str,
    password: str,
    confirm: str
) -> tuple[bool, str]:

    logging.debug(
        f"Валидация: login={login}, "
        f"pwd={mask_password(password)}, "
        f"confirm={mask_password(confirm)}"
    )

    # 1. Логин
    ok, msg = validate_login(login)
    if not ok:
        logging.error(f"Ошибка валидации логина: {msg}")
        return False, msg

    # 2. Пароль
    ok, msg = validate_password(password)
    if not ok:
        logging.error(f"Ошибка валидации пароля: {msg}")
        return False, msg

    # 3. Совпадение
    if password != confirm:
        logging.error("Пароли не совпадают")
        return False, "Пароли не совпадают"

    logging.info(f"Регистрация успешна: login={login}")
    return True, ""