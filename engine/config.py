# -*- coding: utf-8 -*-
"""全局配置：路径、配色、任务元数据。

所有路径使用相对本文件向上两级的项目根目录计算，保证任意工作目录下可运行。
"""
from pathlib import Path

# 项目根目录（engine/ 的上级）
ROOT = Path(__file__).resolve().parent.parent

# 关键目录
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUT = ROOT / "output"
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"

# 主题色（人邮蓝）
BRAND = "#005DA2"
BRAND_DARK = "#00447A"
BRAND_LIGHT = "#E8F1F8"
ACCENT = "#F2A900"        # 强调橙（警示/重点）
OK = "#1E8E5A"            # QA 通过绿
BAD = "#C0392B"           # 失败红
GRAY = "#8A94A0"

# 图表工厂默认
FIG_SIZE = (12.8, 7.2)    # 16:9
DPI = 150

# 任务元数据（编号 -> 名称/章节/说明）；02 为占位
TASKS = {
    1:  {"title": "店铺访客数分析", "chapter": "第1章 大数据时代的统计与数据分析",
         "subtitle": "对比分析 · 趋势分析 · 占比分析", "placeholder": False},
    2:  {"title": "使用八爪鱼采集招聘数据", "chapter": "第2章 数据采集",
         "subtitle": "网页数据采集（需外部采集工具）", "placeholder": True},
    3:  {"title": "数据清洗与加工", "chapter": "第3章 数据处理",
         "subtitle": "缺失值 · 重复值 · 异常值 · 标准化 · 新变量", "placeholder": False},
    4:  {"title": "生产资料市场价格分析", "chapter": "第4章 描述性统计分析",
         "subtitle": "集中趋势 · 离散程度 · 分布形态", "placeholder": False},
    5:  {"title": "小区居民用电分析", "chapter": "第5章 抽样估计分析",
         "subtitle": "总体均值区间估计 · 总体比例区间估计", "placeholder": False},
    6:  {"title": "产品总成本变动分析", "chapter": "第6章 统计指数分析",
         "subtitle": "综合指数 · 平均指数 · 因素分析", "placeholder": False},
    7:  {"title": "研发与销售关系分析", "chapter": "第7章 相关与回归分析",
         "subtitle": "相关分析 · 一元线性回归 · 预测", "placeholder": False},
    8:  {"title": "分析并预测企业总产值", "chapter": "第8章 时间序列分析",
         "subtitle": "发展水平 · 发展速度 · 趋势方程 · 预测", "placeholder": False},
    9:  {"title": "网店访客数可视化展现", "chapter": "第9章 数据可视化展现",
         "subtitle": "统计表 · 柱形图 · 折线图 · 饼图 · 数据透视表", "placeholder": False},
    10: {"title": "制作销售数据分析报告", "chapter": "第10章 制作数据分析报告",
         "subtitle": "分年度分析 · 年度比较 · 总体汇总 · 结论", "placeholder": False},
}

SAMPLE_DATA_NOTICE = ("示例数据，非课程原始数据。本工作台内置的数据按课程文字描述构造，"
                      "用于演示分析流程；教师可替换为真实数据后重跑同一流程。")
