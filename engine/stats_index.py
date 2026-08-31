# -*- coding: utf-8 -*-
"""统计指数（任务 06）：个体指数、综合指数（拉氏/帕氏）、平均指数、因素分析。

教材口径（人邮社《统计与数据分析基础》）：
- 综合指数：拉氏指数以基期为同度量因素；帕氏指数以报告期为同度量因素。
  数量指标（产量 q）综合指数：Kq_拉氏 = Σq₁p₀ / Σq₀p₀；Kq_帕氏 = Σq₁p₁ / Σq₀p₁
  质量指标（单位成本 p）综合指数：Kp_拉氏 = Σp₁q₀ / Σp₀q₀；Kp_帕氏 = Σp₁q₁ / Σp₀q₁
- 平均指数：
  加权算术平均指数（以基期总值为权）：Kq = Σ(i_q·p₀q₀) / Σ(p₀q₀)  ≡ 拉氏数量指数
  加权调和平均指数（以报告期总值为权）：Kp = Σ(p₁q₁) / Σ((p₁q₁)/i_p)  ≡ 帕氏质量指数
- 因素分析（总成本 = 产量 × 单位成本）：
  总成本指数 = 拉氏产量指数 × 帕氏单位成本指数（指数体系自洽）
  绝对额：总成本增减 = Σp₁q₁ − Σp₀q₀ = 产量影响 + 单位成本影响
"""
from __future__ import annotations

import pandas as pd

from . import fmt


def individual_indices(q0, q1, p0, p1) -> list:
    """个体指数：每个产品 i_q = q1/q0、i_p = p1/p0。返回 [(产品, iq, ip)]"""
    out = []
    for a, b, c, d in zip(q0, q1, p0, p1):
        out.append({
            "q0": float(a), "q1": float(b), "p0": float(c), "p1": float(d),
            "iq": float(b / a) if a else float("nan"),
            "ip": float(d / c) if c else float("nan"),
        })
    return out


def _agg_ratio(num: float, den: float) -> float:
    return float(num / den) if den else float("nan")


def composite_indices(q0, q1, p0, p1) -> dict:
    """综合指数：拉氏指数（基期为同度量因素）、帕氏指数（报告期为同度量因素）。

    数量指数（q 为指数化因素，p 为同度量因素）：
      拉氏 Kq_L = Σq₁p₀/Σq₀p₀；帕氏 Kq_P = Σq₁p₁/Σq₀p₁
    质量指数（p 为指数化因素，q 为同度量因素）：
      拉氏 Kp_L = Σp₁q₀/Σp₀q₀；帕氏 Kp_P = Σp₁q₁/Σp₀q₁
    """
    q0, q1, p0, p1 = (list(x) for x in (q0, q1, p0, p1))

    # 四个总额
    s_q0p0 = sum(a * b for a, b in zip(q0, p0))  # 基期总成本
    s_q1p0 = sum(a * b for a, b in zip(q1, p0))  # 报告期产量×基期成本
    s_q0p1 = sum(a * b for a, b in zip(q0, p1))  # 基期产量×报告期成本
    s_q1p1 = sum(a * b for a, b in zip(q1, p1))  # 报告期总成本

    return {
        "s_q0p0": s_q0p0, "s_q1p0": s_q1p0, "s_q0p1": s_q0p1, "s_q1p1": s_q1p1,
        "kq_laspeyres": _agg_ratio(s_q1p0, s_q0p0),   # 拉氏数量指数 Σq₁p₀/Σq₀p₀
        "kp_laspeyres": _agg_ratio(s_q0p1, s_q0p0),   # 拉氏质量指数 Σp₁q₀/Σp₀q₀
        "kq_paasche": _agg_ratio(s_q1p1, s_q0p1),     # 帕氏数量指数 Σq₁p₁/Σq₀p₁
        "kp_paasche": _agg_ratio(s_q1p1, s_q1p0),     # 帕氏质量指数 Σp₁q₁/Σp₀q₁
        # 绝对额影响
        "cost_change": s_q1p1 - s_q0p0,          # 总成本增减
        "q_effect_l": s_q1p0 - s_q0p0,           # 产量影响（拉氏数量口径）
        "p_effect_p": s_q1p1 - s_q1p0,           # 成本影响（帕氏质量口径）
    }


def average_indices(q0, q1, p0, p1) -> dict:
    """平均指数：
    加权算术平均指数（数量，基期总值加权）Kq = Σ(iq·p₀q₀)/Σ(p₀q₀)
    加权调和平均指数（质量，报告期总值加权）Kp = Σ(p₁q₁)/Σ((p₁q₁)/ip)
    """
    s_q0p0 = sum(a * b for a, b in zip(q0, p0))
    s_q1p1 = sum(a * b for a, b in zip(q1, p1))
    num_q = sum((b / a) * (a * c) for a, b, c in zip(q0, q1, p0))
    num_p = sum(a * b for a, b in zip(q1, p1))
    den_p = sum((a * b) / (b / c) for a, b, c in zip(q1, p1, p0)) if p0 else 0
    # 调和平均：Σp₁q₁ / Σ[(p₁q₁)/i_p]，i_p = p1/p0 → (p₁q₁)/(p₁/p₀) = q₁p₀
    den_p = sum(a * c for a, b, c in zip(q1, p1, p0))  # 简化 = Σq₁p₀
    return {
        "kq_arithmetic": _agg_ratio(num_q, s_q0p0),
        "kp_harmonic": _agg_ratio(num_p, den_p),
    }


def factor_analysis(q0, q1, p0, p1) -> dict:
    """因素分析：总成本 = 产量 × 单位成本。指数体系 + 绝对额拆解。"""
    ci = composite_indices(q0, q1, p0, p1)
    ai = average_indices(q0, q1, p0, p1)
    # 指数体系（相对数）：总成本指数 = 拉氏产量指数 × 帕氏成本指数
    k_total = _agg_ratio(ci["s_q1p1"], ci["s_q0p0"])
    k_q = ci["kq_laspeyres"]
    k_p = ci["kp_paasche"]
    product = k_q * k_p
    # 绝对额：总成本增减 = 产量影响 + 成本影响
    total_chg = ci["cost_change"]
    q_eff = ci["q_effect_l"]
    p_eff = ci["p_effect_p"]
    sum_eff = q_eff + p_eff
    return {
        "k_total": k_total,
        "k_q": k_q, "k_p": k_p,
        "product": product,
        "total_chg": total_chg,
        "q_effect": q_eff, "p_effect": p_eff,
        "sum_effect": sum_eff,
        "relative_consistent": abs(k_total - product) < 1e-9,
        "absolute_consistent": abs(total_chg - sum_eff) < 1e-9,
        "ai": ai,
    }


def format_table(q0, q1, p0, p1) -> list:
    """个体指数表行：[产品, q0, q1, iq%, p0, p1, ip%]"""
    return [[f"产品{i+1}", fmt.num(q0[i]), fmt.num(q1[i]), fmt.pct(q1[i] / q0[i] - 1),
             fmt.num(p0[i]), fmt.num(p1[i]), fmt.pct(p1[i] / p0[i] - 1)]
            for i in range(len(q0))]
