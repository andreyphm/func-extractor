import sqlite3
from dataclasses import asdict

from extraction import FunctionInfo


def create_table(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS functions(
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            language TEXT NOT NULL,
            file_path TEXT NOT NULL
        )
        """
    )


def insert_functions(con: sqlite3.Connection, func_list: list[FunctionInfo]) -> None:
    if not func_list:
        return
    cur = con.cursor()
    cur.executemany(
        "INSERT INTO functions VALUES(:name, :code, :language, :file_path)",
        [asdict(func) for func in func_list],
    )
