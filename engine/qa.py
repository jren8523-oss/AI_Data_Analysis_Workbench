# -*- coding: utf-8 -*-
"""QA 验证层：三层验证（数值复算 / 逻辑检查 / 输出一致性）。

每个任务脚本把关键结果交给 QA 检查器，收集 results: [(check_name, passed, detail)]，
渲染进报告尾部；任一 FAIL 不阻断本任务，但记录到 build_log。
"""
from __future__ import annotations

from pathlib import Path


class QA:
    def __init__(self):
        self.results: list = []

    def check(self, name: str, passed: bool, detail: str = "") -> None:
        self.results.append((name, bool(passed), detail or ("通过" if passed else "失败")))

    def approx(self, a, b, tol: float = 1e-6) -> bool:
        """数值近似比对（NaN 视为不相等）。"""
        try:
            return abs(float(a) - float(b)) <= tol
        except (TypeError, ValueError):
            return False

    def has(self, text: str, needle: str) -> bool:
        return needle in text

    def summary(self) -> tuple:
        n_pass = sum(1 for _, p, _ in self.results if p)
        return n_pass, len(self.results)


def check_raw_untouched(name: str, hash_before: str, raw_path: Path) -> bool:
    """校验原始数据文件未被修改（对比构建前记录的哈希）。"""
    import hashlib
    if not raw_path.exists():
        return False
    h = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    return h == hash_before


def find_pngs(out_dir: Path) -> list:
    """列出输出目录下的图表 PNG，用于输出一致性检查。"""
    d = out_dir / "charts"
    if not d.exists():
        return []
    return sorted(d.glob("*.png"))


def png_nonempty(png: Path) -> bool:
    return png.exists() and png.stat().st_size > 0
