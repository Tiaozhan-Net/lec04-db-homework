"""判分项、上下文、结果比较。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from db import norm_rows


@dataclass
class Item:
    part: str
    name: str
    ok: bool
    message: str
    points: float
    maximum: float

    @property
    def lost(self) -> bool:
        return not self.ok


@dataclass
class Ctx:
    root: Path
    submission: Path
    user: str
    verbose: bool = False

    def db_file(self, name: str) -> Path:
        return self.root / "db" / name

    def fixture(self, name: str) -> Path:
        return self.root / "grader" / "fixtures" / name

    def solution(self, name: str) -> Path:
        return self.root / "grader" / "solutions" / name

    def submit(self, *parts: str) -> Path:
        return self.submission.joinpath(*parts)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def diff_result(expected, actual) -> tuple[bool, str]:
    """比较 (列名, 行) 与 (列名, 行)。"""
    expected_columns, expected_rows = expected
    actual_columns, actual_rows = actual

    if [c.lower() for c in expected_columns] != [c.lower() for c in actual_columns]:
        return False, f"列名应为 {expected_columns}，实际是 {actual_columns}"

    expected_norm = norm_rows(expected_rows)
    actual_norm = norm_rows(actual_rows)

    if expected_norm == actual_norm:
        return True, f"{len(actual_norm)} 行，结果正确"

    if len(expected_norm) != len(actual_norm):
        return False, f"行数不对：应为 {len(expected_norm)} 行，实际 {len(actual_norm)} 行" + _preview(
            expected_norm, actual_norm
        )

    for index, (want, got) in enumerate(zip(expected_norm, actual_norm)):
        if want != got:
            return False, f"第 {index + 1} 行不对：应为 {_fmt(want)}，实际 {_fmt(got)}"

    return False, "结果不一致"


def _preview(expected, actual) -> str:
    if not expected and not actual:
        return ""
    return f"（期望前几行 {[_fmt(r) for r in expected[:3]]}，实际前几行 {[_fmt(r) for r in actual[:3]]}）"


def _fmt(row) -> str:
    return "(" + ", ".join(row) + ")"


@dataclass
class PartResult:
    key: str
    title: str
    maximum: float
    items: list[Item] = field(default_factory=list)

    @property
    def score(self) -> float:
        return sum(item.points for item in self.items)

    @property
    def passed(self) -> bool:
        return self.score >= self.maximum
