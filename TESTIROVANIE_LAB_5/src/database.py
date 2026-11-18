import sqlite3
from typing import Optional


class DatabaseRepository:

    MAX_NAME_LEN = 256
    MAX_MESSAGE_LEN = 8096

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_table()


    def _create_table(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id      INTEGER PRIMARY KEY,
                name    TEXT NOT NULL CHECK(length(name) <= 256),
                message TEXT NOT NULL CHECK(length(message) <= 8096)
            )
            """
        )
        self._conn.commit()


    def _validate_message(self, message: str) -> None:
        if not isinstance(message, str):
            raise TypeError("message должен быть строкой")
        if len(message) > self.MAX_MESSAGE_LEN:
            raise ValueError(
                f"Длина message превышает {self.MAX_MESSAGE_LEN} символов"
            )


    def _validate_name(self, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError("name должен быть строкой")
        if not name:
            raise ValueError("name не может быть пустым")
        if len(name) > self.MAX_NAME_LEN:
            raise ValueError(
                f"Длина name превышает {self.MAX_NAME_LEN} символов"
            )

    # ---------- CRUD ----------
    def get_by_id(self, comment_id: int) -> Optional[dict]:
        """Возвращает запись по ID или None."""
        row = self._conn.execute(
            "SELECT id, name, message FROM comments WHERE id = ?",
            (comment_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_by_name(self, username: str) -> list[dict]:
        """Возвращает список записей пользователя username."""
        rows = self._conn.execute(
            "SELECT id, name, message FROM comments WHERE name = ?",
            (username,),
        ).fetchall()
        return [dict(r) for r in rows]

    def add(self, comment_id: int, username: str, message: str) -> bool:
        """Добавляет запись. Возвращает True при успехе.
        Бросает sqlite3.IntegrityError при дублировании ID."""
        if not isinstance(comment_id, int):
            raise TypeError("comment_id должен быть целым числом")
        self._validate_name(username)
        self._validate_message(message)

        try:
            self._conn.execute(
                "INSERT INTO comments (id, name, message) VALUES (?, ?, ?)",
                (comment_id, username, message),
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            # пробрасываем наружу — тест ждёт исключение при дублировании
            raise
        return True

    def update(self, comment_id: int, new_message: str) -> bool:
        """Обновляет message по ID. Возвращает True, если строка найдена."""
        self._validate_message(new_message)
        cur = self._conn.execute(
            "UPDATE comments SET message = ? WHERE id = ?",
            (new_message, comment_id),
        )
        self._conn.commit()
        return cur.rowcount > 0

    def delete(self, comment_id: int) -> bool:
        """Удаляет запись по ID. Возвращает True, если строка была удалена."""
        cur = self._conn.execute(
            "DELETE FROM comments WHERE id = ?", (comment_id,)
        )
        self._conn.commit()
        return cur.rowcount > 0

    # ---------- закрытие ----------
    def close(self) -> None:
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()