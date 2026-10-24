"""SQL 文本工具：去注释、切语句、取第一条关键字。

学生交上来的文件里可能有注释、多行、字符串里带分号，
所以这里用一个小状态机，而不是简单的 split(';')。
"""

from __future__ import annotations

import re

_FIRST_WORD = re.compile(r"\s*([A-Za-z_]+)")


def split_statements(sql: str) -> list[str]:
    """按顶层分号切语句，丢弃注释。"""
    return _split(sql, drop_comments=True)


def split_raw(sql: str) -> list[str]:
    """按顶层分号切语句，保留注释（用于解析 -- @error 1062 这类标记）。"""
    return _split(sql, drop_comments=False)


def has_sql(sql: str) -> bool:
    return bool(split_statements(sql))


def first_keyword(statement: str) -> str:
    match = _FIRST_WORD.match(statement)
    return match.group(1).upper() if match else ""


def _split(sql: str, drop_comments: bool) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    i, n = 0, len(sql)
    in_single = in_double = in_backtick = False

    while i < n:
        ch = sql[i]
        nxt = sql[i + 1] if i + 1 < n else ""

        if not (in_single or in_double or in_backtick):
            if ch == "-" and nxt == "-":
                j = sql.find("\n", i)
                j = n if j == -1 else j
                if not drop_comments:
                    current.append(sql[i:j])
                current.append("\n")
                i = j + 1
                continue
            if ch == "/" and nxt == "*":
                j = sql.find("*/", i + 2)
                j = n if j == -1 else j + 2
                if not drop_comments:
                    current.append(sql[i:j])
                    current.append("\n")
                i = j
                continue
            if ch == "'":
                in_single = True
            elif ch == '"':
                in_double = True
            elif ch == "`":
                in_backtick = True
        else:
            if ch == "\\" and not in_backtick:
                current.append(ch)
                if i + 1 < n:
                    current.append(sql[i + 1])
                    i += 2
                    continue
            elif ch == "'" and in_single:
                in_single = False
            elif ch == '"' and in_double:
                in_double = False
            elif ch == "`" and in_backtick:
                in_backtick = False

        if ch == ";" and not (in_single or in_double or in_backtick):
            statement = "".join(current).strip()
            if statement:
                parts.append(statement)
            current = []
        else:
            current.append(ch)
        i += 1

    statement = "".join(current).strip()
    if statement:
        parts.append(statement)
    return parts
