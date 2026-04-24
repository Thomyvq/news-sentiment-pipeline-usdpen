import sqlite3
from pathlib import Path
from .schema import SCHEMA_SQL

class DB:
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(sqlite_path)
        self.conn.row_factory = sqlite3.Row

    def init(self):
        self.conn.executescript(SCHEMA_SQL)
        self.conn.commit()

    def upsert(self, table: str, row: dict, key: str):
        cols = list(row.keys())
        placeholders = ",".join(["?"] * len(cols))
        col_list = ",".join(cols)
        updates = ",".join([f"{c}=excluded.{c}" for c in cols if c != key])

        sql = f"""
        INSERT INTO {table} ({col_list})
        VALUES ({placeholders})
        ON CONFLICT({key}) DO UPDATE SET {updates};
        """
        self.conn.execute(sql, [row[c] for c in cols])
        self.conn.commit()

    def fetchall(self, sql: str, params=None):
        cur = self.conn.execute(sql, params or [])
        return [dict(r) for r in cur.fetchall()]
