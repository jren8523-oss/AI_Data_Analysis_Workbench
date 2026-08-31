# -*- coding: utf-8 -*-
"""HTML 报告渲染：骨架模板 + 区块拼装 + 讲解要点。

页面为 16:9 截图友好设计（max-width 1280，一屏一块内容），配色人邮蓝。
所有文本/数字由任务脚本传入，本模块只负责排版。
"""
from __future__ import annotations

from pathlib import Path

from . import config

# ---- 内联 SVG 图标库（严禁使用 emoji 当图标） ----
# 16x16 viewBox，使用 currentColor 继承父级 color，便于按上下文染色
_SVG_BULB = '<svg class="ic" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M5 13.5h6v1.2H5zM5.6 12.4l-.7.7-.85-.85.7-.7zM11.95 12.25l-.85-.85.7-.7.85.85zM8 2.5a4.5 4.5 0 0 0-2.5 8.2v.55h5v-.55A4.5 4.5 0 0 0 8 2.5zm-1.2 8.45v.55h2.4v-.55z"/></svg>'
_SVG_WARN = '<svg class="ic" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 1.5 15 14H1zM7.2 6v3.6h1.6V6zm0 4.8v1.4h1.6v-1.4z"/></svg>'
_SVG_CHART = '<svg class="ic" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><rect x="2" y="8" width="2.4" height="6" rx=".4"/><rect x="6" y="5" width="2.4" height="9" rx=".4"/><rect x="10" y="2" width="2.4" height="12" rx=".4"/></svg>'
_SVG_DOC = '<svg class="ic" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M3.5 1.5h7L13 4v10.5H3.5zM4.5 6.5h7M4.5 9h7M4.5 11.5h5"/></svg>'
_SVG_CHECK = '<svg class="ic ic-ok" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M6.5 11.2 3 7.7l1.1-1.1 2.4 2.4 5.4-5.4 1.1 1.1z"/></svg>'
_SVG_CROSS = '<svg class="ic ic-bad" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M3.7 3 8 7.3 12.3 3l.7.7L8.7 8l4.3 4.3-.7.7L8 8.7 3.7 13l-.7-.7L7.3 8 3 3.7z"/></svg>'

_FINDING_BADGE = {
    "事实": ("#005DA2", '<svg class="ic" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><circle cx="8" cy="8" r="5"/></svg>'),
    "分析": ("#F2A900", '<svg class="ic" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><rect x="3" y="3" width="10" height="10" rx="1.5"/></svg>'),
    "推测": ("#B58E1F", '<svg class="ic" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 1.5 14.5 13H1.5z"/></svg>'),
    "建议": ("#1E8E5A", '<svg class="ic" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'),
    "警示": ("#C0392B", _SVG_WARN),
}

_SKELETON = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title} · AI 数据分析工作台</title>
<style>
{css_inline}
</style>
</head>
<body>
<div class="page">
  <div class="top-tag">AI DATA ANALYSIS</div>
  <header class="page-head">
    <div class="head-left">
      <div class="task-tag">任务 {task_no:02d} · {chapter}</div>
      <h1>{task_title}</h1>
      <div class="task-sub">{task_subtitle}</div>
    </div>
    <div class="head-right">
      <div class="logo">AI 数据分析工作台</div>
      <div class="head-date">课堂演示报告 · {date}</div>
    </div>
  </header>

  <div class="sample-banner">{{_SVG_WARN}} {sample_notice}</div>

  <main class="content">
{blocks}
  </main>

  {bottom_note}

  <footer class="page-foot">
    <div class="foot-inner">
      <span>《统计与数据分析基础》 · AI 数据分析工作台</span>
      <span class="qa-summary">{qa_summary}</span>
    </div>
  </footer>
</div>
</body>
</html>
"""


def _esc(s) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def block(title: str, body_html: str, id: str = "") -> str:
    """标准内容块：标题 + 正文。"""
    hid = f' id="{id}"' if id else ""
    return f'<section class="block"{hid}><h2 class="block-title">{_esc(title)}</h2><div class="block-body">{body_html}</div></section>'


def explain(text: str) -> str:
    """讲解要点 callout（老师照着讲）。"""
    return f'<div class="callout"><div class="callout-label">{_SVG_BULB} 讲解要点</div><div class="callout-text">{text}</div></div>'


def warn(text: str) -> str:
    """警示框。"""
    return f'<div class="warn"><div class="warn-label">{_SVG_WARN} 注意事项</div><div class="warn-text">{text}</div></div>'


def table(headers: list, rows: list, caption: str = "", small: bool = False) -> str:
    """HTML 表格。rows 为二维列表。"""
    cls = "tbl small" if small else "tbl"
    cap = f'<caption>{_esc(caption)}</caption>' if caption else ""
    head = "".join(f"<th>{_esc(h)}</th>" for h in headers)
    body = ""
    for r in rows:
        body += "<tr>" + "".join(f"<td>{_esc(c)}</td>" for c in r) + "</tr>"
    return f'<table class="{cls}">{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def formula_box(label: str, formula: str, substitution: str, result: str, interpretation: str = "") -> str:
    """公式四件套卡片：公式 → 代入 → 结果 → 解释。"""
    parts = [
        f'<div class="f-line"><span class="f-label">{_esc(label)}</span><span class="f-formula">{_esc(formula)}</span></div>',
        f'<div class="f-line"><span class="f-label">代入</span><span class="f-sub">{_esc(substitution)}</span></div>',
        f'<div class="f-line"><span class="f-label">结果</span><span class="f-result">{_esc(result)}</span></div>',
    ]
    if interpretation:
        parts.append(f'<div class="f-line"><span class="f-label">解释</span><span class="f-int">{_esc(interpretation)}</span></div>')
    return f'<div class="formula-card">{"".join(parts)}</div>'


def metric_grid(items: list) -> str:
    """指标网格：[(label, value, note)]。"""
    cells = ""
    for label, value, note in items:
        cells += (f'<div class="metric"><div class="metric-label">{_esc(label)}</div>'
                  f'<div class="metric-value">{_esc(value)}</div>'
                  f'<div class="metric-note">{_esc(note)}</div></div>')
    return f'<div class="metric-grid">{cells}</div>'


def figure(img_src: str, caption: str, purpose: str = "", note: str = "") -> str:
    """图表块：图片 + 图注。"""
    cap = f'<figcaption>{_esc(caption)}</figcaption>' if caption else ""
    extra = ""
    if purpose:
        extra += f'<div class="fig-purpose">{_SVG_CHART} {_esc(purpose)}</div>'
    if note:
        extra += f'<div class="fig-note">{_esc(note)}</div>'
    return f'<figure class="fig"><img src="{_esc(img_src)}" alt="{_esc(caption)}">{cap}{extra}</figure>'


def finding(level: str, title: str, text: str) -> str:
    """分层结论行：事实/分析/推测/建议/警示。"""
    color, svg = _FINDING_BADGE.get(level, ("#4A5568", ""))
    style = f' style="color:{color}"' if color else ""
    return (f'<div class="finding f-{level}"><span class="f-badge"{style}>{svg} {_esc(level)}</span>'
            f'<span class="f-title">{_esc(title)}</span><div class="f-text">{_esc(text)}</div></div>')


def qa_block(results: list) -> str:
    """QA 验证区块。results: [(check_name, passed, detail)]"""
    rows = ""
    n_pass = sum(1 for _, p, _ in results if p)
    for name, passed, detail in results:
        icon = _SVG_CHECK if passed else _SVG_CROSS
        cls = "qa-ok" if passed else "qa-fail"
        rows += f'<tr class="{cls}"><td class="qa-icon">{icon}</td><td class="qa-name">{_esc(name)}</td><td>{_esc(detail)}</td></tr>'
    total = len(results)
    summary = f'{n_pass} / {total} 项检查通过'
    return (f'<table class="tbl qa-tbl"><thead><tr><th style="width:48px"></th>'
            f'<th style="width:200px">检查项</th><th>说明</th></tr></thead>'
            f'<tbody>{rows}</tbody></table><div class="qa-total {"" if n_pass == total else "qa-total-fail"}">'
            f'QA 验证：{summary}</div>')


def prompt_box(prompt_text: str, note: str = "") -> str:
    """推荐 Prompt 引述框（对齐参考 PPT）。prompt_text 保留换行。"""
    note_html = f'<div class="prompt-note">{_esc(note)}</div>' if note else ""
    return (f'<div class="prompt-box"><div class="prompt-label">{_SVG_DOC} 推荐 Prompt（学生可复制此提示词，'
            f'自行用 AI 复现同款分析）</div>'
            f'<div class="prompt-text">{_esc(prompt_text)}</div>{note_html}</div>')


def step_card(num, title: str, text: str) -> str:
    """编号步骤卡（对齐参考 PPT 的 1/2/3 步骤卡片）。"""
    return (f'<div class="step-card"><div class="step-num">{num}</div>'
            f'<div class="step-body"><div class="step-title">{_esc(title)}</div>'
            f'<div class="step-text">{_esc(text)}</div></div></div>')


def dig_cards(items: list) -> str:
    """D/I/G 大字母块。items: [(letter, title, text)]"""
    cards = "".join(
        f'<div class="dig-card"><div class="dig-letter">{_esc(l)}</div>'
        f'<div class="dig-title">{_esc(t)}</div><div class="dig-text">{_esc(x)}</div></div>'
        for l, t, x in items
    )
    return f'<div class="dig-grid">{cards}</div>'


def bottom_note(text: str) -> str:
    """底部小结条（对齐参考 PPT 每页底部小结）。"""
    return f'<div class="bottom-note"><span class="bn-label">小结</span><span class="bn-text">{_esc(text)}</span></div>'


def render(task_no: int, blocks: list, out_path: Path, qa_results: list,
           extra_css_rel: str = "",
           bottom_note: str = "") -> None:
    """渲染完整报告页。blocks 为 html 字符串列表；bottom_note 为底部小结条 html。
    CSS 强制内联（保证 file:// 协议下 100% 渲染，不依赖外链）。"""
    meta = config.TASKS[task_no]
    import datetime
    date = datetime.date.today().strftime("%Y-%m-%d")
    n_pass = sum(1 for _, p, _ in qa_results if p)
    total = len(qa_results)
    qa_summary = f"QA {n_pass}/{total} 通过"
    if n_pass != total:
        qa_summary += "（有失败项）"
    # 读取并内联 CSS（file:// 协议下相对路径不稳）
    css_inline = (config.ROOT / "assets" / "css" / "workbench.css").read_text(encoding="utf-8")
    html = _SKELETON.format(
        page_title=f"任务{task_no:02d} {meta['title']}",
        css_inline=css_inline,
        task_no=task_no,
        chapter=meta["chapter"],
        task_title=meta["title"],
        task_subtitle=meta["subtitle"],
        date=date,
        sample_notice=config.SAMPLE_DATA_NOTICE,
        blocks="\n".join(blocks),
        bottom_note=bottom_note,
        qa_summary=qa_summary,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
