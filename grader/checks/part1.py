"""第 1 部分：4 条 DML + 5 条查询。

DML 和查询各用一份快照：
  - DML 跑在 db/00_clean.sql 上，按任务书上的固定值断言；
  - 查询跑在 eval_clean.sql 上，用参考解当场算期望结果。
"""

from __future__ import annotations

import db
from checks.common import Ctx, Item, diff_result, read_text
from sqltext import first_keyword, split_statements

PART = "1"
DML_POINTS = 5
QUERY_POINTS = 3

INSERT_ONE = ("20239001", "2024-1", "软件工程", "90.00", "2025-10-01 09:00:00.000")
BATCH = [
    ("20239002", "张同学", "2023-1", "计算机科学与技术", "77.00", "2025-10-02 10:00:00.000"),
    ("20239003", "李同学", "2023-2", "软件工程", "82.00", "2025-10-02 11:00:00.000"),
    ("20239004", "王同学", "2024-1", "数据科学与大数据技术", "68.00", "2025-10-02 12:00:00.000"),
]
UPDATE_SID = "20230003"
UPDATE_SCORE = "80.00"
DELETE_SID = "20230008"
FINAL_COUNT = 17

QUERIES = [
    ("part1/02_q1.sql", "Q1 条件 + 排序 + 截断", "part1_q1.sql", True),
    ("part1/03_q2.sql", "Q2 前缀匹配", "part1_q2.sql", True),
    ("part1/04_q3.sql", "Q3 排序 + 截断", "part1_q3.sql", True),
    ("part1/05_q4.sql", "Q4 条件计数", "part1_q4.sql", False),
    ("part1/06_q5.sql", "Q5 分组计数", "part1_q5.sql", True),
]

DML_NAMES = ["DML 新增一条", "DML 批量新增三条", "DML 修改一条", "DML 删除一条"]


def run(ctx: Ctx) -> list[Item]:
    items = _dml(ctx)
    items.extend(_queries(ctx))
    return items


def _dml_failed(reason: str) -> list[Item]:
    return [Item(PART, name, False, reason, 0, DML_POINTS) for name in DML_NAMES]


def _dml(ctx: Ctx) -> list[Item]:
    path = ctx.submit("part1", "01_dml.sql")
    if not path.exists():
        return _dml_failed("文件不存在：part1/01_dml.sql")

    conn = db.fresh_db("hw_p1_dml")
    try:
        db.load(conn, ctx.db_file("00_clean.sql"))
        # 同一批人，自增 id 从 101 开始：把 id 写死在 DML 里的会删错行 / 改错行。
        db.load(conn, ctx.fixture("clean_shifted.sql"))
        try:
            db.run_statements(conn, read_text(path))
        except db.ScriptError as exc:
            return _dml_failed(exc.detail())

        return [
            _check_insert_one(conn, ctx),
            _check_batch(conn),
            _check_update(conn),
            _check_delete(conn),
        ]
    finally:
        conn.close()


def _check_insert_one(conn, ctx: Ctx) -> Item:
    sid, class_name, major, score, joined_at = INSERT_ONE
    rows = db.fetch(
        conn,
        "SELECT name, class_name, major, score, joined_at FROM members WHERE student_id = %s",
        (sid,),
    )
    if len(rows) != 1:
        return Item(PART, DML_NAMES[0], False, f"没找到学号 {sid} 的新增记录", 0, DML_POINTS)

    name, got_class, got_major, got_score, got_joined = (db.norm(v) for v in rows[0])
    if name.lower() != ctx.user.lower():
        return Item(
            PART,
            DML_NAMES[0],
            False,
            f"name 应该是你的 GitHub 用户名 {ctx.user}，实际是 {name}",
            0,
            DML_POINTS,
        )
    expected = (class_name, major, score, joined_at)
    actual = (got_class, got_major, got_score, got_joined)
    if expected != actual:
        return Item(
            PART,
            DML_NAMES[0],
            False,
            f"除 name 外的字段应为 {expected}，实际是 {actual}",
            0,
            DML_POINTS,
        )
    return Item(PART, DML_NAMES[0], True, f"学号 {sid} 已写入", DML_POINTS, DML_POINTS)


def _check_batch(conn) -> Item:
    sids = [row[0] for row in BATCH]
    placeholders = ", ".join(["%s"] * len(sids))
    rows = db.fetch(
        conn,
        "SELECT student_id, name, class_name, major, score, joined_at FROM members"
        f" WHERE student_id IN ({placeholders})",
        tuple(sids),
    )
    got = {db.norm(r[0]): tuple(db.norm(v) for v in r[1:]) for r in rows}
    missing = [sid for sid in sids if sid not in got]
    if missing:
        return Item(
            PART, DML_NAMES[1], False, f"缺少这些学号：{', '.join(missing)}", 0, DML_POINTS
        )

    for sid, name, class_name, major, score, joined_at in BATCH:
        expected = (name, class_name, major, score, joined_at)
        if got[sid] != expected:
            return Item(
                PART,
                DML_NAMES[1],
                False,
                f"学号 {sid} 的字段应为 {expected}，实际是 {got[sid]}",
                0,
                DML_POINTS,
            )

    return Item(PART, DML_NAMES[1], True, "三条都在，字段正确", DML_POINTS, DML_POINTS)


def _check_update(conn) -> Item:
    row = db.fetch_one(conn, "SELECT score FROM members WHERE student_id = %s", (UPDATE_SID,))
    if row is None:
        return Item(PART, DML_NAMES[2], False, f"学号 {UPDATE_SID} 被删掉了", 0, DML_POINTS)

    score = db.norm(row[0])
    if score != UPDATE_SCORE:
        return Item(
            PART,
            DML_NAMES[2],
            False,
            f"学号 {UPDATE_SID} 的分数是 {score}，应该是 {UPDATE_SCORE}",
            0,
            DML_POINTS,
        )

    same = db.fetch_one(conn, "SELECT COUNT(*) FROM members WHERE score = %s", (UPDATE_SCORE,))[0]
    if same != 1:
        return Item(
            PART,
            DML_NAMES[2],
            False,
            f"有 {same} 条记录的分数是 {UPDATE_SCORE}，应该只有 1 条（WHERE 写多了？）",
            0,
            DML_POINTS,
        )
    return Item(PART, DML_NAMES[2], True, f"学号 {UPDATE_SID} 已改成 {UPDATE_SCORE}", DML_POINTS, DML_POINTS)


def _check_delete(conn) -> Item:
    left = db.fetch_one(conn, "SELECT COUNT(*) FROM members WHERE student_id = %s", (DELETE_SID,))[0]
    if left != 0:
        return Item(PART, DML_NAMES[3], False, f"学号 {DELETE_SID} 还在", 0, DML_POINTS)

    total = db.fetch_one(conn, "SELECT COUNT(*) FROM members")[0]
    if total != FINAL_COUNT:
        return Item(
            PART,
            DML_NAMES[3],
            False,
            f"删是删了，但表里一共 {total} 行，应该是 {FINAL_COUNT} 行",
            0,
            DML_POINTS,
        )
    return Item(PART, DML_NAMES[3], True, f"学号 {DELETE_SID} 已删除", DML_POINTS, DML_POINTS)


def _queries(ctx: Ctx) -> list[Item]:
    conn = db.fresh_db("hw_p1_q")
    items: list[Item] = []
    try:
        db.load(conn, ctx.db_file("00_clean.sql"))
        db.load(conn, ctx.fixture("eval_clean.sql"))

        for relative, label, solution, need_order in QUERIES:
            items.append(_check_query(conn, ctx, relative, label, solution, need_order))
    finally:
        conn.close()
    return items


def _check_query(conn, ctx: Ctx, relative: str, label: str, solution: str, need_order: bool) -> Item:
    path = ctx.submit(*relative.split("/"))
    if not path.exists():
        return Item(PART, label, False, f"文件不存在：{relative}", 0, QUERY_POINTS)

    statements = split_statements(read_text(path))
    if not statements:
        return Item(PART, label, False, "文件里还没有 SELECT", 0, QUERY_POINTS)
    if len(statements) > 1:
        return Item(PART, label, False, f"只能有一条语句，现在有 {len(statements)} 条", 0, QUERY_POINTS)

    statement = statements[0]
    if first_keyword(statement) not in ("SELECT", "WITH"):
        return Item(PART, label, False, "必须是一条 SELECT", 0, QUERY_POINTS)

    if need_order and "order by" not in statement.lower():
        return Item(PART, label, False, "缺少 ORDER BY", 0, QUERY_POINTS)

    try:
        actual = db.query(conn, statement)
    except Exception as exc:  # noqa: BLE001
        return Item(PART, label, False, f"执行失败：{db.format_error(exc)}", 0, QUERY_POINTS)

    expected = db.query(conn, _solution_statements(ctx, solution)[0])
    ok, message = diff_result(expected, actual)
    return Item(PART, label, ok, message, QUERY_POINTS if ok else 0, QUERY_POINTS)


def _solution_statements(ctx: Ctx, name: str) -> list[str]:
    return split_statements(read_text(ctx.solution(name)))
