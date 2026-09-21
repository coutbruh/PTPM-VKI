import os
import sys
import logging


def setup_logging() -> None:
    os.makedirs("logs", exist_ok=True)

    log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/file_txt.log", encoding="utf-8")
        ]
    )


def main() -> None:
    setup_logging()
    logging.info("Логгер сконфигурирован")
    logging.info("Приложение запущено")

    try:
        login = input("Введите логин: ").strip()
        password = input("Введите пароль: ")
        confirm = input("Подтвердите пароль: ")

        from validator import validate_registration
        ok, message = validate_registration(login, password, confirm)

        if ok:
            print("True")
            print("")
        else:
            print("False")
            print(message)

    except KeyboardInterrupt:
        logging.warning("Прервано пользователем")
    except Exception:
        logging.exception("Критическая ошибка:")
        raise


if __name__ == "__main__":
    main()