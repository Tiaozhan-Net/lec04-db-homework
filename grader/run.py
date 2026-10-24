#!/usr/bin/env python3
"""课后作业自动评测入口。

用法：
    python grader/run.py --part 3
    python grader/run.py --part all --user Alice
    python grader/run.py --part 1,2 --submission submissions/Alice

CI 上由 .github/workflows/autograde.yml 调用，参数一样。
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
import traceback
from pathlib import Path

GRADER_ROOT = Path(__file__).resolve().parent
REPO_ROOT = GRADER_ROOT.parent
sys.path.insert(0, str(GRADER_ROOT))

import db  # noqa: E402
from checks.common import Ctx, Item, PartResult  # noqa: E402

PARTS = [
    ("1", "第 1 部分 会用：CRUD 与基础查询", "checks.part1", 35),
    ("2", "第 2 部分 看得懂：脏数据诊断", "checks.part2", 20),
    ("3", "第 3 部分 洗得干净：清洗", "checks.part3", 25),
    ("4", "第 4 部分 拦得住：约束与报错", "checks.part4", 10),
    ("5", "第 5 部分 删得回来：软删除迁移", "checks.part5", 10),
]
BONUS = ("B", "加分 看得见：索引与执行计划", "checks.bonus", 10)

PASS_LINE = 50


def main() -> int:
    _soften_console()
    args = _parse_args()
    selected = _select(args.part)

    if not args.submission and not args.user:
        print("用 --user 指定 GitHub 用户名，或者用 --submission 指定目录", file=sys.stderr)
        return 2

    submission = Path(args.submission) if args.submission else REPO_ROOT / "submissions" / args.user
    if not submission.is_absolute():
        submission = (REPO_ROOT / submission).resolve()
    if not submission.exists():
        print(f"找不到提交目录：{submission}", file=sys.stderr)
        return 2

    user = (args.user or submission.name).strip()
    if not user:
        print("缺少 --user", file=sys.stderr)
        return 2

    try:
        version = _mysql_version()
    except Exception as exc:  # noqa: BLE001
        print(f"连不上 MySQL：{db.format_error(exc)}", file=sys.stderr)
        print("先看 docs/00-环境搭建.md，确认数据库已经起来。", file=sys.stderr)
        return 2

    ctx = Ctx(root=REPO_ROOT, submission=submission, user=user, verbose=args.verbose)

    results: list[PartResult] = []
    for key, title, module_name, maximum in PARTS + [BONUS]:
        if key not in selected:
            continue
        results.append(_run_part(key, title, module_name, maximum, ctx))

    report = _render(results, user, version, selected)
    print(report)

    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(report + "\n")

    return 0


def _soften_console() -> None:
    """管道/GBK 控制台下打印 ✅ 会 UnicodeEncodeError，降级成问号就好。"""
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:  # noqa: BLE001
        pass


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="数据库课后作业评测")
    parser.add_argument("--part", default="all", help="all / 1 / 2 / 3 / 4 / 5 / bonus，可以逗号分隔")
    parser.add_argument("--user", default=os.getenv("GITHUB_USER", ""), help="GitHub 用户名")
    parser.add_argument("--submission", default=os.getenv("SUBMISSION_DIR", ""), help="提交目录")
    parser.add_argument("--verbose", action="store_true", help="打印完整异常")
    return parser.parse_args()


def _select(value: str) -> set[str]:
    text = (value or "all").strip().lower()
    if text == "all":
        return {key for key, *_ in PARTS} | {BONUS[0]}
    wanted = set()
    for piece in text.replace(" ", "").split(","):
        if not piece:
            continue
        wanted.add("B" if piece in ("b", "bonus", "加分") else piece)
    unknown = wanted - ({key for key, *_ in PARTS} | {BONUS[0]})
    if unknown:
        raise SystemExit(f"不认识的 --part：{', '.join(sorted(unknown))}")
    return wanted


def _mysql_version() -> str:
    conn = db.connect()
    try:
        _, rows = db.query(conn, "SELECT VERSION()")
        return rows[0][0]
    finally:
        conn.close()


def _run_part(key: str, title: str, module_name: str, maximum: float, ctx: Ctx) -> PartResult:
    try:
        module = importlib.import_module(module_name)
        items = module.run(ctx)
    except Exception as exc:  # noqa: BLE001
        if ctx.verbose:
            traceback.print_exc()
        items = [
            Item(
                key,
                "评测异常",
                False,
                f"{type(exc).__name__}: {exc}（这是评测脚本的问题，不是你的 SQL 的问题，请联系老师）",
                0,
                maximum,
            )
        ]
    return PartResult(key=key, title=title, maximum=maximum, items=items)


def _render(results: list[PartResult], user: str, version: str, selected: set[str]) -> str:
    lines = [
        "## 自动评测结果",
        "",
        f"GitHub 用户：`{user}`　MySQL：{version}",
        "",
        "| 部分 | 得分 |",
        "| --- | ---: |",
    ]

    for result in results:
        lines.append(f"| {result.title} | {_num(result.score)} / {_num(result.maximum)} |")

    mandatory = [r for r in results if r.key != BONUS[0]]
    bonus = [r for r in results if r.key == BONUS[0]]
    full_run = {r.key for r in results} >= {key for key, *_ in PARTS}

    if mandatory:
        total = sum(r.score for r in mandatory)
        maximum = sum(r.maximum for r in mandatory)
        if full_run:
            lines.append(f"| **必做合计** | **{_num(total)} / {_num(maximum)}** |")
        else:
            lines.append(f"| 本次必做小计 | {_num(total)} / {_num(maximum)} |")
    if bonus:
        lines.append(f"| 加分（单独统计） | {_num(bonus[0].score)} / {_num(bonus[0].maximum)} |")

    lines.append("")
    if full_run:
        total = sum(r.score for r in mandatory)
        lines.append(f"**{'及格' if total >= PASS_LINE else '未及格'}**（及格线 {PASS_LINE} 分）")
    else:
        missing = [key for key, *_ in PARTS if key not in selected]
        if missing:
            lines.append(f"本次只跑了第 {', '.join(sorted(selected))} 部分，其余部分没有算进总分。")
    lines.append("")

    for result in results:
        lines.extend(_render_part(result))

    return "\n".join(lines).rstrip() + "\n"


def _render_part(result: PartResult) -> list[str]:
    lines = [
        f"### {result.title}",
        "",
        "| 项目 | 结果 | 说明 | 得分 |",
        "| --- | --- | --- | ---: |",
    ]
    for item in result.items:
        mark = "✅" if item.ok else "❌"
        lines.append(
            f"| {_cell(item.name)} | {mark} | {_cell(item.message)} | "
            f"{_num(item.points)} / {_num(item.maximum)} |"
        )
    lines.append("")
    return lines


def _cell(text: str) -> str:
    value = str(text).replace("|", "\\|").replace("\n", " ")
    return value if len(value) <= 240 else value[:240] + " ..."


def _num(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


if __name__ == "__main__":
    raise SystemExit(main())
