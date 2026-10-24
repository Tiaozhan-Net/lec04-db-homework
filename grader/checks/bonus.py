"""加分部分：B1 函数索引（4 分）+ B2 索引预算（6 分）。

两题都跑在 20 万行的 hw_bonus 上，只看执行计划，不看 SQL 文本。
"""

from __future__ import annotations

import json

import db
from checks.common import Ctx, Item, read_text
from sqltext import first_keyword, split_statements

PART = "B"

B1_POINTS = 4

TARGETS = [
    (
        "B2 Q1 学号 + 活跃",
        "SELECT id, name FROM members"
        " WHERE student_id = '90000001' AND deleted_at IS NULL",
        ["student_id"],
        1,
    ),
    (
        "B2 Q2 专业 + 分数",
        "SELECT id FROM members WHERE major = '计算机科学与技术' AND score >= 60"
        " ORDER BY score DESC LIMIT 20",
        ["major", "score"],
        2,
    ),
    (
        "B2 Q3 班级 + 时间",
        "SELECT id FROM members WHERE class_name = '2023-1' ORDER BY joined_at",
        ["class_name", "joined_at"],
        2,
    ),
    (
        "B2 Q4 专业 + 姓名前缀",
        "SELECT id FROM members WHERE major = '软件工程' AND name LIKE '张%'",
        ["major", "name"],
        1,
    ),
]


def run(ctx: Ctx) -> list[Item]:
    conn = db.fresh_db("hw_bonus")
    try:
        db.load(conn, ctx.db_file("02_big.sql"))
        items = [_b1(conn, ctx)]
        items.extend(_b2(conn, ctx))
        return items
    finally:
        conn.close()


def _b1(conn, ctx: Ctx) -> Item:
    path = ctx.submit("bonus", "b1_functional_key.sql")
    if not path.exists():
        return Item(PART, "B1 让函数键参与定位", False, "文件不存在：bonus/b1_functional_key.sql", 0, B1_POINTS)

    statements = split_statements(read_text(path))
    if not statements:
        return Item(PART, "B1 让函数键参与定位", False, "文件里还没有 SELECT", 0, B1_POINTS)
    if len(statements) > 1:
        return Item(PART, "B1 让函数键参与定位", False, "只能有一条 SELECT", 0, B1_POINTS)
    if first_keyword(statements[0]) not in ("SELECT", "WITH"):
        return Item(PART, "B1 让函数键参与定位", False, "必须是一条 SELECT", 0, B1_POINTS)

    try:
        plan = _explain(conn, statements[0])
    except Exception as exc:  # noqa: BLE001
        return Item(PART, "B1 让函数键参与定位", False, f"EXPLAIN 失败：{db.format_error(exc)}", 0, B1_POINTS)

    node = _table_node(plan)
    if node is None:
        return Item(PART, "B1 让函数键参与定位", False, "执行计划里没有找到表访问节点", 0, B1_POINTS)

    key = node.get("key")
    parts = node.get("used_key_parts")
    count = len(parts) if isinstance(parts, list) else 0

    if key is None:
        return Item(
            PART,
            "B1 让函数键参与定位",
            False,
            f"走的是全表扫描，没有用上索引（used_key_parts={parts}）",
            0,
            B1_POINTS,
        )
    if count != 2:
        return Item(
            PART,
            "B1 让函数键参与定位",
            False,
            f"用了索引 {key}，但只用到 {count} 段（used_key_parts={parts}）。"
            "WHERE 里的表达式要和 05b 建索引时写的一模一样",
            0,
            B1_POINTS,
        )

    return Item(
        PART,
        "B1 让函数键参与定位",
        True,
        f"索引 {key}，用了 2 段",
        B1_POINTS,
        B1_POINTS,
    )


def _b2(conn, ctx: Ctx) -> list[Item]:
    path = ctx.submit("bonus", "b2_indexes.sql")
    if not path.exists():
        return _b2_failed("文件不存在：bonus/b2_indexes.sql")

    before = _index_count(conn)
    try:
        db.run_statements(conn, read_text(path))
    except db.ScriptError as exc:
        return _b2_failed(f"索引脚本执行失败：{exc.detail()}")

    db.try_execute(conn, "ANALYZE TABLE members")

    after = _index_count(conn)
    added = after - before
    if added > 3:
        return _b2_failed(f"新增了 {added} 个索引，题目要求最多 3 个（第一条查询用现成的唯一索引）")

    indexes = _indexes(conn)
    items: list[Item] = []
    for label, sql, prefix, points in TARGETS:
        items.append(_check_plan(conn, label, sql, prefix, points, indexes, added))
    return items


def _b2_failed(reason: str) -> list[Item]:
    return [Item(PART, label, False, reason, 0, points) for label, _sql, _prefix, points in TARGETS]


def _check_plan(conn, label, sql, prefix, points, indexes, added) -> Item:
    try:
        plan = _explain(conn, sql)
    except Exception as exc:  # noqa: BLE001
        return Item(PART, label, False, f"EXPLAIN 失败：{db.format_error(exc)}", 0, points)

    node = _table_node(plan)
    if node is None:
        return Item(PART, label, False, "执行计划里没有找到表访问节点", 0, points)

    key = node.get("key")
    candidates = [name for name, cols in indexes.items() if cols[: len(prefix)] == prefix]
    filesort = _has_filesort(plan)

    if key is None:
        return Item(PART, label, False, f"走的是全表扫描；期望用上 {tuple(prefix)} 开头的索引", 0, points)
    if key not in candidates:
        return Item(
            PART,
            label,
            False,
            f"用的是索引 {key}，期望 {tuple(prefix)} 开头的索引（现有候选：{candidates or '无'}）",
            0,
            points,
        )
    if filesort:
        return Item(PART, label, False, f"用上了 {key}，但还有 filesort", 0, points)

    return Item(PART, label, True, f"用上 {key}，没有 filesort", points, points)


def _index_count(conn) -> int:
    row = db.fetch_one(
        conn,
        "SELECT COUNT(DISTINCT INDEX_NAME) FROM information_schema.STATISTICS"
        " WHERE TABLE_SCHEMA = 'hw_bonus' AND TABLE_NAME = 'members' AND INDEX_NAME <> 'PRIMARY'",
    )
    return row[0] if row else 0


def _indexes(conn) -> dict[str, list]:
    rows = db.fetch(
        conn,
        "SELECT INDEX_NAME, COLUMN_NAME FROM information_schema.STATISTICS"
        " WHERE TABLE_SCHEMA = 'hw_bonus' AND TABLE_NAME = 'members' AND INDEX_NAME <> 'PRIMARY'"
        " ORDER BY INDEX_NAME, SEQ_IN_INDEX",
    )
    grouped: dict[str, list] = {}
    for index_name, column in rows:
        grouped.setdefault(index_name, []).append(column)
    return grouped


def _explain(conn, sql: str) -> dict:
    statement = sql.strip().rstrip(";")
    _, rows = db.query(conn, "EXPLAIN FORMAT=JSON " + statement)
    return json.loads(rows[0][0])


def _table_node(plan):
    stack = [plan]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if "access_type" in node and "table_name" in node:
                return node
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return None


def _has_filesort(plan) -> bool:
    stack = [plan]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if node.get("using_filesort") is True:
                return True
            filesort = node.get("filesort")
            if isinstance(filesort, dict) and filesort.get("using_filesort"):
                return True
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return False
