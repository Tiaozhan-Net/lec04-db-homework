"""第 2 部分：6 条只读诊断查询。

跑在 eval_legacy 上，期望结果由参考解当场算出来。
"""

from __future__ import annotations

import db
from checks.common import Ctx, Item, diff_result, read_text
from sqltext import first_keyword, split_statements

PART = "2"
POINTS = 3
ALL_BONUS = 2

QUERIES = [
    ("part2/q1_dup.sql", "Q1 重复学号", "part2_q1.sql"),
    ("part2/q2_name.sql", "Q2 姓名不干净", "part2_q2.sql"),
    ("part2/q3_score.sql", "Q3 分数越界", "part2_q3.sql"),
    ("part2/q4_date.sql", "Q4 日期格式", "part2_q4.sql"),
    ("part2/q5_whitelist.sql", "Q5 专业/班级白名单", "part2_q5.sql"),
    ("part2/q6_sid.sql", "Q6 学号不是 8 位数字", "part2_q6.sql"),
]


def run(ctx: Ctx) -> list[Item]:
    conn = db.fresh_db("hw_p2")
    items: list[Item] = []
    try:
        db.load(conn, ctx.db_file("01_legacy.sql"))
        db.load(conn, ctx.fixture("eval_legacy.sql"))

        for relative, label, solution in QUERIES:
            items.append(_check(conn, ctx, relative, label, solution))
    finally:
        conn.close()

    if all(item.ok for item in items):
        items.append(Item(PART, "六条全对", True, "列名、排序、结果都正确", ALL_BONUS, ALL_BONUS))
    else:
        items.append(Item(PART, "六条全对", False, "六条都对了才有这 2 分", 0, ALL_BONUS))
    return items


def _check(conn, ctx: Ctx, relative: str, label: str, solution: str) -> Item:
    path = ctx.submit(*relative.split("/"))
    if not path.exists():
        return Item(PART, label, False, f"文件不存在：{relative}", 0, POINTS)

    statements = split_statements(read_text(path))
    if not statements:
        return Item(PART, label, False, "文件里还没有 SELECT", 0, POINTS)
    if len(statements) > 1:
        return Item(PART, label, False, f"只能有一条语句，现在有 {len(statements)} 条", 0, POINTS)

    statement = statements[0]
    if first_keyword(statement) not in ("SELECT", "WITH"):
        return Item(PART, label, False, "必须是一条只读的 SELECT", 0, POINTS)
    if "order by" not in statement.lower():
        return Item(PART, label, False, "缺少 ORDER BY", 0, POINTS)

    try:
        actual = db.query(conn, statement)
    except Exception as exc:  # noqa: BLE001
        return Item(PART, label, False, f"执行失败：{db.format_error(exc)}", 0, POINTS)

    expected = db.query(conn, split_statements(read_text(ctx.solution(solution)))[0])
    ok, message = diff_result(expected, actual)
    return Item(PART, label, ok, message, POINTS if ok else 0, POINTS)
