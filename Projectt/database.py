import sqlite3
import logging

class RegistrationDB:

    def __init__(self,db_path:str="memory"):
        self._conn=sqlite3.Connection(db_path)
        self._conn.row_factory=sqlite3.Row
        self._create_table()

    def _create_table(self)->None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                login      TEXT NOT NULL,
                password   TEXT NOT NULL,
                confirm    TEXT NOT NULL,
                result     INTEGER NOT NULL,
                error_msg  TEXT,
                PRIMARY KEY (login, password, confirm)
            )
            """)
        self._conn.commit()
    def add(self, login:str, password:str,confirm:str,result:bool,error_msg="")->None:
        logging.debug("DB add: login=%s",login)
        self._conn.execute(
            "INSERT OR REPLACE INTO registrations"
            "(login,password,confirm,result,error_msg) VALUES(?,?,?,?,?)",
            (login,password,confirm,int(result),error_msg),
                           )
        self._conn.commit()

#--------------------
    def get(self, login: str, password: str, confirm: str):
        """Возвращает (result: bool, error_msg: str) или None."""
        cur = self._conn.execute(
            "SELECT result, error_msg FROM registrations "
            "WHERE login=? AND password=? AND confirm=?",
            (login, password, confirm),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return bool(row["result"]), row["error_msg"] or ""

    def delete(self, login: str, password: str, confirm: str) -> bool:
        cur = self._conn.execute(
            "DELETE FROM registrations WHERE login=? AND password=? AND confirm=?",
            (login, password, confirm),
        )
        self._conn.commit()
        return cur.rowcount > 0

    def close(self) -> None:
        self._conn.close()