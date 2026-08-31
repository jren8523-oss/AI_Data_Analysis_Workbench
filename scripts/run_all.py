# -*- coding: utf-8 -*-
"""全量构建脚本：依次运行 9 个任务脚本（02 占位跳过），输出到 output/taskNN/report.html。

用法（项目根目录下）：
    python scripts/run_all.py
结果写入 output/build_log.json，控制台打印 PASS/FAIL 汇总。
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

# 保证 scripts/ 下运行时也能导入根目录的 engine / tasks 包
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import config, pipeline


def main() -> None:
    log: dict = {"tasks": []}
    # 02 为占位任务（需外部采集工具），记录 SKIP 不参与构建
    log["tasks"].append({
        "task": 2, "status": "SKIP", "checks": 0, "passed": 0,
        "time_s": 0.0, "error": "占位任务：需外部采集工具（八爪鱼），不参与构建",
    })
    specs = [
        (1, "tasks.task01_visitors"),
        (3, "tasks.task03_cleaning"),
        (4, "tasks.task04_price_desc"),
        (5, "tasks.task05_sampling"),
        (6, "tasks.task06_index"),
        (7, "tasks.task07_regression"),
        (8, "tasks.task08_timeseries"),
        (9, "tasks.task09_vis_viz"),
        (10, "tasks.task10_report"),
    ]
    for task_no, mod_name in specs:
        mod = importlib.import_module(mod_name)
        out_dir = config.OUTPUT / f"task{task_no:02d}"
        pipeline.run_task(task_no, mod.build, out_dir, log)

    pipeline.write_log(log, config.OUTPUT / "build_log.json")
    pipeline.print_summary(log)
    return log


if __name__ == "__main__":
    main()
