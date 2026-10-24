"""第 5 部分：软删除迁移。

跑在"清洗 + 加约束"之后的黄金库上。
学生交 05a / 05b / 05c 三个脚本，按顺序执行，每一步都做行为测试。
"""

from __future__ import annotations

import db
from checks.common import Ctx, Item, read_text

PART = "5"
TARGET_SID = "20230002"

INSERT_ACTIVE = (
    "INSERT INTO members (student_id, name, class_name, major, score, joined_at)"
    " VALUES ('%s', '%s', '2023-1', '软件工程', 60.00, '2025-12-01 00:00:00')"
)


def run(ctx: Ctx) -> list[Item]:
    conn = _golden(ctx)
    try:
        a_path = ctx.submit("part5", "05a_softdelete.sql")
        if not a_path.exists():
            return _all_failed("文件不存在：part5/05a_softdelete.sql")
        try:
            db.run_statements(conn, read_text(a_path))
        except db.ScriptError as exc:
            return _all_failed(f"05a 执行失败：{exc.detail()}")

        items = _check_05a(conn)

        # 这一步只写进报告，不计分：让"问题先发生"。
        with db.rollback_after(conn):
            probe = db.try_execute(conn, INSERT_ACTIVE % (TARGET_SID, "抢先报名"))
        if probe is None:
            items.append(
                Item(
                    PART,
                    "（不计分）迁移前插同号活跃行",
                    False,
                    "居然插进去了，说明 05a 没加上 deleted_at 或者唯一索引已经不对了",
                    0,
                    0,
                )
            )
        elif probe[0] != 1062:
            items.append(
                Item(
                    PART,
                    "（不计分）迁移前插同号活跃行",
                    False,
                    f"按预期应该报 1062，实际是 {probe[0]}：{probe[1]}",
                    0,
                    0,
                )
            )
        else:
            items.append(
                Item(
                    PART,
                    "（不计分）迁移前插同号活跃行",
                    True,
                    "按预期报了 1062，旧行还占着学号——这就是下面要解决的问题",
                    0,
                    0,
                )
            )

        b_path = ctx.submit("part5", "05b_migrate.sql")
        if not b_path.exists():
            items.extend(_later_failed("文件不存在：part5/05b_migrate.sql"))
            return items
        try:
            db.run_statements(conn, read_text(b_path))
        except db.ScriptError as exc:
            items.extend(_later_failed(f"05b 执行失败：{exc.detail()}"))
            return items

        items.append(_check_index(conn))
        items.append(_check_new_active(conn))

        c_path = ctx.submit("part5", "05c_reinsert.sql")
        if not c_path.exists():
            items.append(Item(PART, "05c 用同一学号重新报名", False, "文件不存在：part5/05c_reinsert.sql", 0, 2))
            items.append(Item(PART, "恢复旧行时仍然冲突", False, "05c 没交，先不判", 0, 2))
            return items
        try:
            db.run_statements(conn, read_text(c_path))
        except db.ScriptError as exc:
            items.append(Item(PART, "05c 用同一学号重新报名", False, exc.detail(), 0, 2))
            items.append(Item(PART, "恢复旧行时仍然冲突", False, "05c 执行失败，先不判", 0, 2))
            return items

        items.append(_check_reinsert(conn))
        items.append(_check_restore_conflict(conn))
        return items
    finally:
        conn.close()


def _golden(ctx: Ctx):
    conn = db.fresh_db("hw_p5")
    db.load(conn, ctx.db_file("01_legacy.sql"))
    db.load(conn, ctx.fixture("eval_legacy.sql"))
    db.run_statements(conn, read_text(ctx.solution("part3_clean.sql")))
    db.run_statements(conn, read_text(ctx.solution("part4_constraints.sql")))
    return conn


def _all_failed(reason: str) -> list[Item]:
    items = [
        Item(PART, "05a 加 deleted_at 列", False, reason, 0, 1),
        Item(PART, "05a 软删除指定那条", False, reason, 0, 1),
        Item(PART, "05a 其余行不动", False, reason, 0, 1),
    ]
    items.extend(_later_failed(reason))
    return items


def _later_failed(reason: str) -> list[Item]:
    return [
        Item(PART, "05b 活跃行才唯一", False, reason, 0, 2),
        Item(PART, "05b 同号新活跃行可插入", False, reason, 0, 1),
        Item(PART, "05c 用同一学号重新报名", False, reason, 0, 2),
        Item(PART, "恢复旧行时仍然冲突", False, reason, 0, 2),
    ]


def _check_05a(conn) -> list[Item]:
    column = db.fetch_one(
        conn,
        "SELECT DATA_TYPE FROM information_schema.COLUMNS"
        " WHERE TABLE_SCHEMA = 'hw_p5' AND TABLE_NAME = 'members' AND COLUMN_NAME = 'deleted_at'",
    )
    items = [
        Item(
            PART,
            "05a 加 deleted_at 列",
            column is not None,
            "列已存在" if column else "members 表里没有 deleted_at 列",
            1 if column else 0,
            1,
        )
    ]

    soft = db.fetch_one(
        conn,
        "SELECT COUNT(*) FROM members WHERE student_id = %s AND deleted_at IS NOT NULL",
        (TARGET_SID,),
    )[0]
    items.append(
        Item(
            PART,
            "05a 软删除指定那条",
            soft == 1,
            f"学号 {TARGET_SID} 有 {soft} 条被标记为已取消，应该是 1 条",
            1 if soft == 1 else 0,
            1,
        )
    )

    total = db.fetch_one(conn, "SELECT COUNT(*) FROM members")[0]
    active = db.fetch_one(conn, "SELECT COUNT(*) FROM members WHERE deleted_at IS NULL")[0]
    ok = total == 14 and active == 13
    items.append(
        Item(
            PART,
            "05a 其余行不动",
            ok,
            f"一共 {total} 行（应为 14），其中活跃 {active} 行（应为 13）",
            1 if ok else 0,
            1,
        )
    )
    return items


def _index_parts(conn):
    rows = db.fetch(
        conn,
        "SELECT INDEX_NAME, COLUMN_NAME, EXPRESSION FROM information_schema.STATISTICS"
        " WHERE TABLE_SCHEMA = 'hw_p5' AND TABLE_NAME = 'members'"
        "   AND NON_UNIQUE = 0 AND INDEX_NAME <> 'PRIMARY'"
        " ORDER BY INDEX_NAME, SEQ_IN_INDEX",
    )
    grouped: dict[str, list[tuple[str | None, str | None]]] = {}
    for index_name, column, expression in rows:
        grouped.setdefault(index_name, []).append((column, expression))
    return grouped


def _check_index(conn) -> Item:
    grouped = _index_parts(conn)
    target = None
    for name, parts in grouped.items():
        if len(parts) < 2:
            continue
        if parts[0][0] != "student_id":
            continue
        if parts[1][1] or parts[1][0]:
            target = name
            break

    if target is None:
        return Item(
            PART,
            "05b 活跃行才唯一",
            False,
            "没有找到 (student_id, 活跃标记) 两段的唯一索引",
            0,
            2,
        )

    with db.rollback_after(conn):
        duplicate = db.try_execute(conn, INSERT_ACTIVE % ("20230001", "重复报名"))

    if duplicate is None:
        return Item(
            PART,
            "05b 活跃行才唯一",
            False,
            "索引建了，但两条活跃行同学号还能插进去——索引没起作用",
            0,
            2,
        )
    if duplicate[0] != 1062:
        return Item(
            PART,
            "05b 活跃行才唯一",
            False,
            f"两条活跃行同学号报的是 {duplicate[0]}，应该是 1062",
            0,
            2,
        )

    return Item(PART, "05b 活跃行才唯一", True, "两段唯一索引已生效", 2, 2)


def _check_new_active(conn) -> Item:
    with db.rollback_after(conn):
        db.try_execute(
            conn, "UPDATE members SET deleted_at = NOW(3) WHERE student_id = '20230001'"
        )
        result = db.try_execute(conn, INSERT_ACTIVE % ("20230001", "重新报名"))

    ok = result is None
    return Item(
        PART,
        "05b 同号新活跃行可插入",
        ok,
        "旧行软删除后，同学号可以重新报名" if ok else f"还是插不进去：{result[1] if result else ''}",
        1 if ok else 0,
        1,
    )


def _check_reinsert(conn) -> Item:
    active = db.fetch_one(
        conn,
        "SELECT COUNT(*) FROM members WHERE student_id = %s AND deleted_at IS NULL",
        (TARGET_SID,),
    )[0]
    total = db.fetch_one(conn, "SELECT COUNT(*) FROM members")[0]
    if active == 1 and total == 15:
        return Item(PART, "05c 用同一学号重新报名", True, "新的活跃行已经写进去，旧的软删除行还在", 2, 2)
    return Item(
        PART,
        "05c 用同一学号重新报名",
        False,
        f"学号 {TARGET_SID} 的活跃行有 {active} 条（应为 1），全表 {total} 行（应为 15）",
        0,
        2,
    )


def _check_restore_conflict(conn) -> Item:
    with db.rollback_after(conn):
        db.try_execute(
            conn, "UPDATE members SET deleted_at = NOW(3) WHERE student_id = '20230001'"
        )
        inserted = db.try_execute(conn, INSERT_ACTIVE % ("20230001", "新的活跃行"))
        restore = db.try_execute(
            conn,
            "UPDATE members SET deleted_at = NULL WHERE student_id = '20230001' AND deleted_at IS NOT NULL",
        )

    if inserted is not None:
        return Item(
            PART,
            "恢复旧行时仍然冲突",
            False,
            f"软删除之后同号新活跃行插不进去：{inserted[1]}",
            0,
            2,
        )
    if restore is None:
        return Item(
            PART,
            "恢复旧行时仍然冲突",
            False,
            "把旧的已删除行恢复成活跃，居然成功了——说明唯一约束没兜住",
            0,
            2,
        )
    if restore[0] != 1062:
        return Item(
            PART,
            "恢复旧行时仍然冲突",
            False,
            f"恢复旧行报的是 {restore[0]}，应该是 1062",
            0,
            2,
        )
    return Item(PART, "恢复旧行时仍然冲突", True, "报出 1062，行为正确", 2, 2)
