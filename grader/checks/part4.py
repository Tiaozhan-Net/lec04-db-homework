"""第 4 部分：加约束 + 预测报错。

跑在"已清洗好的黄金库"上（参考解洗过的 eval_legacy），
学生只交 DDL 和四条必错语句。
"""

from __future__ import annotations

import re

import db
from checks.common import Ctx, Item, read_text
from sqltext import split_raw, split_statements

PART = "4"
STRUCTURE_POINTS = 1
ERROR_POINTS = 1

NOT_NULL_COLUMNS = ["student_id", "name", "class_name", "major", "score", "joined_at"]

BEHAVIOUR_SQL = {
    "姓名全是空格": "INSERT INTO members (student_id, name, class_name, major, score, joined_at)"
    " VALUES ('99900001', '   ', '2023-1', '软件工程', 60.00, '2025-12-01 00:00:00')",
    "分数 101": "INSERT INTO members (student_id, name, class_name, major, score, joined_at)"
    " VALUES ('99900002', '测试乙', '2023-1', '软件工程', 101.00, '2025-12-01 00:00:00')",
    "分数 -1": "INSERT INTO members (student_id, name, class_name, major, score, joined_at)"
    " VALUES ('99900003', '测试丙', '2023-1', '软件工程', -1.00, '2025-12-01 00:00:00')",
    "学号只有 7 位": "INSERT INTO members (student_id, name, class_name, major, score, joined_at)"
    " VALUES ('1234567', '测试丁', '2023-1', '软件工程', 60.00, '2025-12-01 00:00:00')",
    "专业写成同义词": "INSERT INTO members (student_id, name, class_name, major, score, joined_at)"
    " VALUES ('99900005', '测试戊', '2023-1', '计算机', 60.00, '2025-12-01 00:00:00')",
    "班级格式不对": "INSERT INTO members (student_id, name, class_name, major, score, joined_at)"
    " VALUES ('99900006', '测试己', '2023-1班', '软件工程', 60.00, '2025-12-01 00:00:00')",
}

ERROR_RE = re.compile(r"@error\s+(\d+)")


def run(ctx: Ctx) -> list[Item]:
    conn = db.fresh_db("hw_p4")
    try:
        db.load(conn, ctx.db_file("01_legacy.sql"))
        db.load(conn, ctx.fixture("eval_legacy.sql"))
        db.run_statements(conn, read_text(ctx.solution("part3_clean.sql")))

        ddl_path = ctx.submit("part4", "constraints.sql")
        if not ddl_path.exists():
            return _all_failed("文件不存在：part4/constraints.sql")
        try:
            db.run_statements(conn, read_text(ddl_path))
        except db.ScriptError as exc:
            return _all_failed(exc.detail())

        items = _structure(conn)
        items.append(_behaviour(conn, "姓名与分数必须被拦住", ["姓名全是空格", "分数 101", "分数 -1"], 1))
        items.append(_behaviour(conn, "学号、专业、班级必须被拦住", ["学号只有 7 位", "专业写成同义词", "班级格式不对"], 1))
        items.extend(_errors(conn, ctx))
        return items
    finally:
        conn.close()


def _all_failed(reason: str) -> list[Item]:
    items = [
        Item(PART, "六列 NOT NULL", False, reason, 0, STRUCTURE_POINTS),
        Item(PART, "学号唯一索引", False, reason, 0, STRUCTURE_POINTS),
        Item(PART, "joined_at 改成 DATETIME(3)", False, reason, 0, STRUCTURE_POINTS),
        Item(PART, "score 改成 DECIMAL(5,2)", False, reason, 0, STRUCTURE_POINTS),
        Item(PART, "姓名与分数必须被拦住", False, reason, 0, 1),
        Item(PART, "学号、专业、班级必须被拦住", False, reason, 0, 1),
    ]
    for code in (1062, 1048, 1364, 3819):
        items.append(Item(PART, f"预测 {code}", False, reason, 0, ERROR_POINTS))
    return items


def _columns(conn):
    rows = db.fetch(
        conn,
        "SELECT COLUMN_NAME, IS_NULLABLE, DATA_TYPE, DATETIME_PRECISION,"
        " NUMERIC_PRECISION, NUMERIC_SCALE"
        " FROM information_schema.COLUMNS"
        " WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'members'",
        ("hw_p4",),
    )
    return {row[0]: row[1:] for row in rows}


def _structure(conn) -> list[Item]:
    info = _columns(conn)
    items: list[Item] = []

    missing = [name for name in NOT_NULL_COLUMNS if name not in info]
    if missing:
        items.append(Item(PART, "六列 NOT NULL", False, f"缺少列：{', '.join(missing)}", 0, 1))
    else:
        nullable = [name for name in NOT_NULL_COLUMNS if info[name][0] != "NO"]
        items.append(
            Item(
                PART,
                "六列 NOT NULL",
                not nullable,
                "六列都已 NOT NULL" if not nullable else f"这些列还可空：{', '.join(nullable)}",
                1 if not nullable else 0,
                1,
            )
        )

    indexes = db.fetch(
        conn,
        "SELECT INDEX_NAME, SEQ_IN_INDEX, COLUMN_NAME"
        " FROM information_schema.STATISTICS"
        " WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'members'"
        "   AND NON_UNIQUE = 0 AND INDEX_NAME <> 'PRIMARY'"
        " ORDER BY INDEX_NAME, SEQ_IN_INDEX",
        ("hw_p4",),
    )
    grouped: dict[str, list[str]] = {}
    for index_name, _seq, column in indexes:
        grouped.setdefault(index_name, []).append(column or "")

    unique_sid = [name for name, cols in grouped.items() if cols and cols[0] == "student_id"]
    items.append(
        Item(
            PART,
            "学号唯一索引",
            bool(unique_sid),
            f"找到唯一索引 {unique_sid[0]}" if unique_sid else "没有找到第一列是 student_id 的唯一索引",
            1 if unique_sid else 0,
            1,
        )
    )

    # info[列名] = (IS_NULLABLE, DATA_TYPE, DATETIME_PRECISION, NUMERIC_PRECISION, NUMERIC_SCALE)
    joined = info.get("joined_at")
    ok = bool(joined) and joined[1] == "datetime" and joined[2] == 3
    items.append(
        Item(
            PART,
            "joined_at 改成 DATETIME(3)",
            ok,
            "类型正确" if ok else f"现在是 {joined[1] if joined else '缺失'}，精度 {joined[2] if joined else '-'}",
            1 if ok else 0,
            1,
        )
    )

    score = info.get("score")
    ok = bool(score) and score[1] == "decimal" and score[3] == 5 and score[4] == 2
    items.append(
        Item(
            PART,
            "score 改成 DECIMAL(5,2)",
            ok,
            "类型正确" if ok else f"现在是 {score[1] if score else '缺失'}({score[3] if score else '-'},{score[4] if score else '-'})",
            1 if ok else 0,
            1,
        )
    )
    return items


def _behaviour(conn, label: str, cases: list[str], points: float) -> Item:
    failures = []
    for case in cases:
        with db.rollback_after(conn):
            result = db.try_execute(conn, BEHAVIOUR_SQL[case])
        if result is None:
            failures.append(f"{case}：居然插入成功了")
        elif result[0] != 3819:
            failures.append(f"{case}：报的是 {result[0]}，应该是 3819")

    ok = not failures
    return Item(
        PART,
        label,
        ok,
        "三条都被拦住了" if ok else "；".join(failures),
        points if ok else 0,
        points,
    )


def _errors(conn, ctx: Ctx) -> list[Item]:
    path = ctx.submit("part4", "errors.sql")
    if not path.exists():
        return [
            Item(PART, f"预测 {code}", False, "文件不存在：part4/errors.sql", 0, ERROR_POINTS)
            for code in (1062, 1048, 1364, 3819)
        ]

    found: dict[int, str] = {}
    for chunk in split_raw(read_text(path)):
        match = ERROR_RE.search(chunk)
        if not match:
            continue
        statements = split_statements(chunk)
        if not statements:
            continue
        found[int(match.group(1))] = statements[0]

    items: list[Item] = []
    for expected in (1062, 1048, 1364, 3819):
        statement = found.get(expected)
        if statement is None:
            items.append(
                Item(
                    PART,
                    f"预测 {expected}",
                    False,
                    f"没有找到 -- @error {expected} 那条语句（注释要写在语句正上方）",
                    0,
                    ERROR_POINTS,
                )
            )
            continue

        with db.rollback_after(conn):
            result = db.try_execute(conn, statement)

        if result is None:
            message = "这条语句居然执行成功了，没有被拦住"
            ok = False
        elif result[0] != expected:
            message = f"期望 {expected}，实际报的是 {result[0]}"
            ok = False
        else:
            message = f"报出 {expected}，正确"
            ok = True

        items.append(Item(PART, f"预测 {expected}", ok, message, ERROR_POINTS if ok else 0, ERROR_POINTS))
    return items
