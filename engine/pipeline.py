# -*- coding: utf-8 -*-
"""流水线编排：任务脚本 -> 指标 dict -> 图表 -> 报告 -> QA -> build_log。

run_all.py 调用本模块全量构建 9 个任务（02 占位跳过）。
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from . import config, qa as qa_mod


def run_task(task_no: int, build_fn, out_dir: Path, log: dict) -> dict:
    """执行单个任务：build_fn() 应返回 qa.QA 实例并完成报告渲染。

    build_fn 签名: build_fn(out_dir) -> qa.QA
    """
    t0 = time.time()
    entry = {"task": task_no, "status": "RUNNING", "checks": 0, "passed": 0,
             "time_s": 0.0, "error": ""}
    try:
        qa_obj = build_fn(out_dir)
        n_pass, n_total = qa_obj.summary()
        entry.update(status="PASS" if n_pass == n_total else "FAIL",
                     checks=n_total, passed=n_pass)
        if n_pass != n_total:
            entry["failed_checks"] = [name for name, p, _ in qa_obj.results if not p]
    except Exception as e:  # noqa: BLE001 —— 记录失败但继续其他任务
        import traceback
        entry.update(status="ERROR", error=f"{type(e).__name__}: {e}\n{traceback.format_exc()[-800:]}")
    entry["time_s"] = round(time.time() - t0, 2)
    log["tasks"].append(entry)
    return entry


def write_log(log: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def print_summary(log: dict) -> None:
    print("=" * 46)
    print("AI 数据分析工作台 · 全量构建结果")
    print("=" * 46)
    for e in log["tasks"]:
        flag = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥", "SKIP": "⏭"}.get(e["status"], "•")
        extra = ""
        if e["status"] == "PASS":
            extra = f"（{e['passed']}/{e['checks']} 检查通过）"
        elif e.get("failed_checks"):
            extra = f" 失败项: {e['failed_checks']}"
        print(f"  任务{e['task']:02d}  {flag} {e['status']:<6} {e['time_s']:>6.2f}s{extra}")
    n_pass = sum(1 for e in log["tasks"] if e["status"] == "PASS")
    n_total = len(log["tasks"])
    print("=" * 46)
    print(f"  通过 {n_pass}/{n_total}  （02 为占位任务不参与构建）")
    print("=" * 46)
