"""MySQL 连接、会话设置、脚本执行、结果规范化。

会话口径固定在这里，本地和 CI 必须一致：
  - sql_mode 用 MySQL 8.0 的默认严格模式（否则 1364 不会报错）
  - 字符集 utf8mb4 / 排序规则 utf8mb4_0900_ai_ci（NO PAD，尾部空格有意义）
  - 时区 +00:00
"""

from __future__ import annotations

import os
import re
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pymysql
from pymysql.constants import CLIENT

from sqltext import split_statements

SQL_MODE = (
    "ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,"
    "ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION"
)
CHARSET = "utf8mb4"
COLLATION = "utf8mb4_0900_ai_ci"
QUERY_TIMEOUT_MS = 15000

_DB_NAME = re.compile(r"^[A-Za-z0-9_]+$")


class ScriptError(Exception):
    """学生脚本里第 index 条语句执行失败。"""

    def __init__(self, index: int, statement: str, original: Exception):
        self.index = index
        self.statement = statement
        self.original = original
        super().__init__(format_error(original))

    def detail(self) -> str:
        preview = " ".join(self.statement.split())
        if len(preview) > 120:
            preview = preview[:120] + " ..."
        return f"第 {self.index} 条语句失败：{format_error(self.original)}｜{preview}"


def format_error(exc: BaseException) -> str:
    if isinstance(exc, pymysql.MySQLError) and exc.args:
        code = exc.args[0]
        message = exc.args[1] if len(exc.args) > 1 else ""
        return f"ERROR {code}: {message}"
    return f"{type(exc).__name__}: {exc}"


def errno_of(exc: BaseException) -> int | None:
    if isinstance(exc, pymysql.MySQLError) and exc.args:
        try:
            return int(exc.args[0])
        except (TypeError, ValueError):
            return None
    return None


def _connection_kwargs(database: str | None) -> dict:
    kwargs = dict(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        charset=CHARSET,
        autocommit=True,
        connect_timeout=10,
    )
    if database:
        kwargs["database"] = database
    return kwargs


def connect(database: str | None = None) -> pymysql.connections.Connection:
    conn = pymysql.connect(**_connection_kwargs(database))
    with conn.cursor() as cur:
        cur.execute("SET SESSION sql_mode = %s", (SQL_MODE,))
        cur.execute("SET SESSION time_zone = '+00:00'")
        cur.execute("SET SESSION max_execution_time = %s", (QUERY_TIMEOUT_MS,))
    return conn


def reset_database(name: str) -> None:
    if not _DB_NAME.match(name):
        raise ValueError(f"非法库名：{name}")
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS `{name}`")
            cur.execute(
                f"CREATE DATABASE `{name}` CHARACTER SET {CHARSET} COLLATE {COLLATION}"
            )
    finally:
        conn.close()


def fresh_db(name: str) -> pymysql.connections.Connection:
    """重建一个空库并连上去。"""
    reset_database(name)
    return connect(name)


def load(conn, path: Path) -> None:
    run_statements(conn, Path(path).read_text(encoding="utf-8-sig"))


def run_statements(conn, text: str) -> int:
    """逐条执行，返回执行的语句条数。出错抛 ScriptError。"""
    statements = split_statements(text)
    if not statements:
        raise ScriptError(0, "", RuntimeError("文件里没有可执行的 SQL"))

    for index, statement in enumerate(statements, start=1):
        try:
            with conn.cursor() as cur:
                cur.execute(statement)
                while True:
                    if cur.description:
                        cur.fetchall()
                    if not cur.nextset():
                        break
        except pymysql.MySQLError as exc:
            raise ScriptError(index, statement, exc) from exc

    conn.commit()
    return len(statements)


def query(conn, sql: str, args=None) -> tuple[list[str], list[tuple]]:
    with conn.cursor() as cur:
        cur.execute(sql, args)
        columns = [item[0] for item in cur.description] if cur.description else []
        rows = list(cur.fetchall()) if cur.description else []
    return columns, rows


def fetch(conn, sql: str, args=None) -> list[tuple]:
    return query(conn, sql, args)[1]


def fetch_one(conn, sql: str, args=None):
    rows = fetch(conn, sql, args)
    return rows[0] if rows else None


def try_execute(conn, sql: str) -> tuple[int, str] | None:
    """执行一条语句：成功返回 None，失败返回 (errno, message)。"""
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            while True:
                if cur.description:
                    cur.fetchall()
                if not cur.nextset():
                    break
        return None
    except pymysql.MySQLError as exc:
        return errno_of(exc) or -1, format_error(exc)


@contextmanager
def rollback_after(conn):
    """在一个事务里跑测试，结束无论成功失败都回滚。"""
    with conn.cursor() as cur:
        cur.execute("START TRANSACTION")
    try:
        yield
    finally:
        with conn.cursor() as cur:
            cur.execute("ROLLBACK")


def table_identity(conn, database: str, table: str = "members"):
    """InnoDB 内部表 id：表被重建过，这个值会变。"""
    try:
        row = fetch_one(
            conn,
            "SELECT TABLE_ID FROM information_schema.INNODB_TABLES WHERE NAME = %s",
            (f"{database}/{table}",),
        )
        return row[0] if row else None
    except pymysql.MySQLError:
        return None


def norm(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def norm_rows(rows) -> list[tuple[str, ...]]:
    return [tuple(norm(value) for value in row) for row in rows]
