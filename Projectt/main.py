# main.py
import os
import sys
import logging

from controller import Controller
from database import RegistrationDB
from notifier import FakeEmailNotifier
from user_io import ConsoleUserIO
from validator import Validator


def setup_logging() -> None:
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | [%(levelname)-7s] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/file_txt.log", encoding="utf-8"),
        ],
    )


def main() -> None:
    setup_logging()
    controller = Controller(
        user_io=ConsoleUserIO(),
        db=RegistrationDB("registrations.db"),
        notifier=FakeEmailNotifier(),
        validator=Validator(),
    )
    try:
        controller.run_registration()
    except KeyboardInterrupt:
        logging.warning("Прервано пользователем")
    except Exception:
        logging.exception("Критическая ошибка:")
        raise


if __name__ == "__main__":
    main()