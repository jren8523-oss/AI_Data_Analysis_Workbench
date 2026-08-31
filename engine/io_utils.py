# -*- coding: utf-8 -*-
"""CSV 读写：UTF-8-sig（Excel 直开不乱码）、raw 只读守卫、示例数据标注。"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from . import config


def read_csv(name: str, **kwargs) -> pd.DataFrame:
    """读取 data/raw/{name}.csv，兼容 UTF-8 / UTF-8-sig / GBK 编码。"""
    path = config.DATA_RAW / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"示例数据不存在: {path}")
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return pd.read_csv(path, encoding=enc, **kwargs)
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"无法解码文件 {path.name}，请确认编码")


def read_csv_path(path: Path, **kwargs) -> pd.DataFrame:
    """读取任意路径 CSV（带 BOM 兼容）。"""
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return pd.read_csv(path, encoding=enc, **kwargs)
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"无法解码文件 {path.name}")


def write_csv(df: pd.DataFrame, name: str, subdir: str = "") -> Path:
    """写 data/processed 下的 CSV，UTF-8-sig。返回写入路径。"""
    if subdir:
        d = config.DATA_PROCESSED / subdir
    else:
        d = config.DATA_PROCESSED
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def raw_hash(name: str) -> str:
    """原始数据文件 SHA-256，供 QA 校验原始数据未被修改。"""
    path = config.DATA_RAW / f"{name}.csv"
    return sha256(path)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()
