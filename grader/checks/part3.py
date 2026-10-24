"""第 3 部分：清洗（硬删除）。

跑在 eval_legacy 上，期望终态由参考解当场算出来。
按维度给分，每个维度全对才给。
"""

from __future__ import annotations

import re

import db
from checks.common import Ctx, Item, read_text
from sqltext import split_statements

PART = "3"

DIMENSIONS = [
    ("行数", 5, None),
    ("学号", 5, (0,)),
    ("姓名", 4, (2,)),
    ("班级/专业", 5, (3, 4)),
    ("分数", 3, (5,)),
    ("日期", 3, (6,)),
]

FORBIDDEN = re.compile(r"\b(drop\s+table|drop\s+database|truncate)\b", re.IGNORECASE)

SNAPSHOT_SQL = """
SELECT student_id,
       TRIM(student_id) AS sid_key,
       name, class_name, major, score, joined_at
FROM members
ORDER BY sid_key, id
"""


def run(ctx: Ctx) -> list[Item]:
    expected = _expected_snapshot(ctx)
    path = ctx.submit("part3", "clean.sql")
    if not path.exists():
        return _all_failed(f"文件不存在：part3/clean.sql")

    text = read_text(path)
    if FORBIDDEN.search(" ".join(split_statements(text))):
        return _all_failed("第 3 部分禁止 DROP TABLE / TRUNCATE / 重建表，只能用 UPDATE / DELETE 原地清洗")

    conn = db.fresh_db("hw_p3")
    try:
        db.load(conn, ctx.db_file("01_legacy.sql"))
        db.load(conn, ctx.fixture("eval_legacy.sql"))

        before = db.table_identity(conn, "hw_p3")
        try:
            db.run_statements(conn, text)
        except db.ScriptError as exc:
            return _all_failed(exc.detail())

        after = db.table_identity(conn, "hw_p3")
        if before and after and before != after:
            return _all_failed("检测到 members 表被重建了。第 3 部分要求原地清洗，不能建新表再改名")

        try:
            actual = _snapshot(conn)
        except Exception as exc:  # noqa: BLE001
            return _all_failed(f"清洗后读不出 members 表：{db.format_error(exc)}")
    finally:
        conn.close()

    return _score(expected, actual)


def _expected_snapshot(ctx: Ctx):
    ref = db.fresh_db("hw_p3_ref")
    try:
        db.load(ref, ctx.db_file("01_legacy.sql"))
        db.load(ref, ctx.fixture("eval_legacy.sql"))
        db.run_statements(ref, read_text(ctx.solution("part3_clean.sql")))
        return _snapshot(ref)
    finally:
        ref.close()


def _snapshot(conn):
    columns, rows = db.query(conn, SNAPSHOT_SQL)
    if not columns:
        raise RuntimeError("members 表不存在")
    return [tuple(db.norm(value) for value in row) for row in rows]


def _all_failed(reason: str) -> list[Item]:
    return [Item(PART, name, False, reason, 0, points) for name, points, _ in DIMENSIONS]


def _score(expected, actual) -> list[Item]:
    items: list[Item] = []
    same_length = len(expected) == len(actual)

    for name, points, indices in DIMENSIONS:
        if not same_length:
            items.append(
                Item(
                    PART,
                    name,
                    False,
                    f"行数不对：应为 {len(expected)} 行，实际 {len(actual)} 行，其余维度先不判",
                    0,
                    points,
                )
            )
            continue

        if indices is None:
            items.append(Item(PART, name, True, f"{len(actual)} 行", points, points))
            continue

        want = [tuple(row[i] for i in indices) for row in expected]
        got = [tuple(row[i] for i in indices) for row in actual]
        if want == got:
            items.append(Item(PART, name, True, "正确", points, points))
        else:
            items.append(Item(PART, name, False, _first_diff(want, got, name), 0, points))

    return items


def _first_diff(want, got, name: str) -> str:
    for index, (a, b) in enumerate(zip(want, got)):
        if a != b:
            return f"第 {index + 1} 行{name}：应为 {a}，实际 {b}"
    return f"{name}不一致"
