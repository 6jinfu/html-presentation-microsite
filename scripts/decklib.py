#!/usr/bin/env python3
"""Validate a report deck and render a self-contained HTML presentation."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "references" / "deck.schema.json"
TOKENS_PATH = ROOT / "assets" / "tokens.json"
CSS_PATH = ROOT / "assets" / "deck.css"
JS_PATH = ROOT / "assets" / "deck.js"

REMOTE_RE = re.compile(r"(?:https?:)?//", re.I)
PLACEHOLDER_RE = re.compile(r"(\{\{|\}\}|\[DATA NEEDED\]|\bTODO\b|\bLorem\b|\blorem\b)")
ID_RE = re.compile(r"^[a-z][a-z0-9-]{0,31}$")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def schema():
    return load_json(SCHEMA_PATH)


def tokens():
    return load_json(TOKENS_PATH)


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def validate(deck: dict) -> list[str]:
    errors: list[str] = []
    spec = schema()
    limits = spec["limits"]
    if not isinstance(deck, dict):
        return ["deck.json 必须是对象"]
    meta = deck.get("meta")
    slides = deck.get("slides")
    if not isinstance(meta, dict):
        errors.append("缺少 meta 对象")
        meta = {}
    if not isinstance(slides, list):
        errors.append("缺少 slides 数组")
        slides = []

    required_meta = [
        "title", "lang", "mode", "theme", "density", "audience", "venue",
        "decision", "narrative", "formats", "footer",
    ]
    for key in required_meta:
        if key not in meta:
            errors.append(f"meta.{key} 缺失")

    check_text(errors, "meta.title", meta.get("title"), "doc_title", limits)
    check_text(errors, "meta.audience", meta.get("audience"), "audience", limits)
    check_text(errors, "meta.venue", meta.get("venue"), "venue", limits)
    check_text(errors, "meta.decision", meta.get("decision"), "decision", limits)
    check_text(errors, "meta.narrative", meta.get("narrative"), "narrative", limits)
    check_text(errors, "meta.footer", meta.get("footer"), "footer", limits)

    if meta.get("lang") not in spec["languages"]:
        errors.append("meta.lang 只接受 zh-CN 或 en")
    mode = meta.get("mode")
    if mode not in spec["modes"]:
        errors.append("meta.mode 只接受 showcase 或 report")
    theme_names = tokens()["themes"]
    if meta.get("theme") not in theme_names:
        errors.append("meta.theme 不在 assets/tokens.json")
    if meta.get("density") not in tokens()["density"]:
        errors.append("meta.density 只接受 calm、standard 或 compact")

    formats = meta.get("formats")
    if not isinstance(formats, list) or not formats:
        errors.append("meta.formats 至少要包含 html")
    else:
        if "html" not in formats:
            errors.append("meta.formats 必须包含 html")
        for item in formats:
            if item == "pptx":
                errors.append("本技能不生成可编辑 PPTX。formats 只能是 html 或 pdf")
            elif item not in spec["formats"]:
                errors.append(f"不支持的格式：{item}")

    gaps = meta.get("gaps", [])
    if gaps is None:
        gaps = []
    if not isinstance(gaps, list):
        errors.append("meta.gaps 必须是字符串数组")
        gaps = []
    for i, gap in enumerate(gaps):
        check_text(errors, f"meta.gaps[{i}]", gap, "gap", limits)

    if mode in spec["modes"]:
        low, high = spec["modes"][mode]
        if not (low <= len(slides) <= high):
            errors.append(f"{mode} 模式需要 {low}-{high} 页，当前是 {len(slides)} 页")

    seen = set()
    layouts = []
    for index, slide in enumerate(slides):
        where = f"slides[{index}]"
        if not isinstance(slide, dict):
            errors.append(f"{where} 必须是对象")
            continue
        layout = slide.get("layout")
        layouts.append(layout)
        if layout not in spec["layouts"]:
            errors.append(f"{where}.layout 不受支持：{layout}")
            continue
        slide_id = slide.get("id")
        if not isinstance(slide_id, str) or not ID_RE.match(slide_id):
            errors.append(f"{where}.id 需要小写英文和连字符")
        elif slide_id in seen:
            errors.append(f"重复的 slides id：{slide_id}")
        else:
            seen.add(slide_id)
        validate_slide(errors, where, slide, spec["layouts"][layout], limits, spec["topicLabels"])

    if slides:
        if "cover" not in layouts:
            errors.append("至少需要一页 cover")
        if "close" not in layouts:
            errors.append("至少需要一页 close")
    return errors


def validate_slide(errors, where, slide, rule, limits, topic_labels):
    for key in rule["required"]:
        if key not in slide:
            errors.append(f"{where} 缺少 {key}")
    lines = slide.get("title_lines")
    low, high = rule["title_lines"]
    if not isinstance(lines, list) or not (low <= len(lines) <= high):
        errors.append(f"{where}.title_lines 需要 {low}-{high} 行")
    else:
        for i, line in enumerate(lines):
            check_text(errors, f"{where}.title_lines[{i}]", line, "title_line", limits)
        joined = "".join(lines) if all(isinstance(line, str) for line in lines) else ""
        if joined in topic_labels or (joined and len(joined) < 6):
            errors.append(f"{where} 的标题要写成判断句，不能只写「{joined or '空'}」")
    optional_text = {
        "kicker": "kicker",
        "subtitle": "subtitle",
        "meta": "meta_line",
        "callout": "callout",
        "statement": "statement",
        "aside": "aside",
        "ask": "ask",
        "note": "note",
        "verdict": "verdict",
        "index": "index",
    }
    for key, limit_name in optional_text.items():
        if key in slide:
            check_text(errors, f"{where}.{key}", slide.get(key), limit_name, limits)

    items_key = rule.get("itemsKey", "items")
    if "items" in rule:
        items = slide.get(items_key)
        low, high = rule["items"]
        if not isinstance(items, list) or not (low <= len(items) <= high):
            errors.append(f"{where}.{items_key} 需要 {low}-{high} 项")
            items = []
        for i, item in enumerate(items):
            item_where = f"{where}.{items_key}[{i}]"
            if not isinstance(item, dict):
                errors.append(f"{item_where} 必须是对象")
                continue
            for field in rule.get("itemRequired", []):
                if field not in item:
                    errors.append(f"{item_where} 缺少 {field}")
            check_item_fields(errors, item_where, slide["layout"], item, limits)

    if slide.get("layout") == "comparison":
        for side in ("left", "right"):
            block = slide.get(side)
            side_where = f"{where}.{side}"
            if not isinstance(block, dict):
                errors.append(f"{side_where} 必须是对象")
                continue
            check_text(errors, f"{side_where}.title", block.get("title"), "item_title", limits)
            points = block.get("points")
            if not isinstance(points, list) or not (2 <= len(points) <= 4):
                errors.append(f"{side_where}.points 需要 2-4 条")
            else:
                for i, point in enumerate(points):
                    check_text(errors, f"{side_where}.points[{i}]", point, "point", limits)

    if slide.get("layout") == "metrics":
        for i, item in enumerate(slide.get("items") or []):
            if isinstance(item, dict) and "bar" in item:
                bar = item["bar"]
                if not isinstance(bar, int) or isinstance(bar, bool) or not (0 <= bar <= 100):
                    errors.append(f"{where}.items[{i}].bar 需要 0 到 100 的整数")


def check_item_fields(errors, where, layout, item, limits):
    mapping = {
        "agenda": {"index": "index", "title": "item_title", "summary": "summary"},
        "thesis": {"title": "item_title", "body": "item_body"},
        "metrics": {"value": "metric_value", "label": "metric_label", "note": "metric_note"},
        "cards": {"index": "index", "title": "item_title", "body": "item_body"},
        "roadmap": {"title": "phase_title", "window": "phase_window", "body": "phase_body"},
        "summary": {"title": "item_title", "body": "item_body"},
        "close": {"title": "item_title", "body": "item_body"},
    }
    for field, limit_name in mapping.get(layout, {}).items():
        if field in item:
            check_text(errors, f"{where}.{field}", item.get(field), limit_name, limits)


def check_text(errors, where, value, limit_name, limits):
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{where} 需要非空字符串")
        return
    if PLACEHOLDER_RE.search(value):
        errors.append(f"{where} 含有未替换的占位或待补标记")
    limit = limits[limit_name]
    if len(value) > limit:
        errors.append(f"{where} 超过 {limit} 个字符（当前 {len(value)}）")


def lint_html(page: str, deck: dict | None = None) -> list[str]:
    errors = []
    if REMOTE_RE.search(page):
        errors.append("HTML 引用了外部地址。交付文件必须离线自包含")
    if PLACEHOLDER_RE.search(page):
        errors.append("HTML 仍有占位符、TODO、Lorem 或 [DATA NEEDED]")
    for marker in ("overflow: hidden", "min-width: 0", "@page", "13.333in 7.5in"):
        if marker not in page:
            errors.append(f"HTML 缺少版式标记：{marker}")
    if deck is None:
        return errors
    slides = deck["slides"]
    found = re.findall(r'data-layout="([^"]+)"', page)
    if found != [slide["layout"] for slide in slides]:
        errors.append("HTML 的页面顺序或版式与 deck.json 不一致")
    for slide in slides:
        for line in slide["title_lines"]:
            if f">{esc(line)}<" not in page and esc(line) not in page:
                errors.append(f"HTML 缺少标题行：{line}")
    footer = deck["meta"]["footer"]
    if page.count(esc(footer)) < len(slides):
        errors.append("页脚没有出现在每一页")
    plain = re.sub(r"<[^>]+>", "", page)
    for gap in deck["meta"].get("gaps", []):
        if gap not in plain:
            errors.append(f"缺口没有写进成稿：{gap}")
    return errors


def render(deck: dict) -> str:
    errors = validate(deck)
    if errors:
        raise ValueError("\n".join(errors))
    theme_block = theme_css(tokens())
    css = CSS_PATH.read_text(encoding="utf-8")
    script = JS_PATH.read_text(encoding="utf-8")
    meta = deck["meta"]
    total = len(deck["slides"])
    sections = []
    for index, slide in enumerate(deck["slides"]):
        sections.append(render_slide(slide, index, total, meta["footer"]))
    description = esc(meta["narrative"])
    title = esc(meta["title"])
    return f"""<!DOCTYPE html>
<html lang="{esc(meta['lang'])}" data-theme="{esc(meta['theme'])}" data-density="{esc(meta['density'])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="html-presentation-microsite">
<title>{title}</title>
<meta name="description" content="{description}">
<style>
{theme_block}
{css}
</style>
</head>
<body>
<a class="skip" href="#stage">跳到幻灯片</a>
<div class="viewport">
  <div class="stage" id="stage">
    <div class="progress" style="width: {100 / total:.4f}%"></div>
    <p class="live sr" aria-live="polite"></p>
    {''.join(sections)}
  </div>
</div>
<script>
{script}
</script>
</body>
</html>
"""


def theme_css(data: dict) -> str:
    fonts = data["fonts"]
    lines = [
        ":root {",
        f"  --display: {fonts['display']};",
        f"  --body: {fonts['body']};",
        f"  --mono: {fonts['mono']};",
        "}",
    ]
    for name, theme in data["themes"].items():
        lines.append(f'html[data-theme="{name}"] {{')
        for key, value in theme.items():
            lines.append(f"  --{key}: {value};")
        lines.append("}")
    for name, density in data["density"].items():
        lines.append(f'html[data-density="{name}"] {{')
        lines.append(f"  --pad-x: {density['padX']}px;")
        lines.append(f"  --pad-y: {density['padY']}px;")
        lines.append(f"  --title: {density['title']}px;")
        lines.append(f"  --gap: {density['gap']}px;")
        lines.append("}")
    return "\n".join(lines)


def render_slide(slide, index, total, footer) -> str:
    layout = slide["layout"]
    hidden = "" if index == 0 else " hidden"
    active = " is-active" if index == 0 else ""
    label = "，".join(slide["title_lines"])
    body = {
        "cover": render_cover,
        "agenda": render_agenda,
        "chapter": render_chapter,
        "thesis": render_thesis,
        "metrics": render_metrics,
        "comparison": render_comparison,
        "cards": render_cards,
        "roadmap": render_roadmap,
        "summary": render_summary,
        "close": render_close,
    }[layout](slide)
    kicker = slide.get("kicker") or layout_kicker(layout)
    return (
        f'<section class="slide layout-{layout}{active}" data-layout="{layout}" '
        f'data-id="{esc(slide["id"])}" aria-label="{esc(label)}"{hidden}>'
        f'<div class="slide-canvas"><div class="frame" data-fit>'
        f'<header class="mast"><p class="kicker" data-fit>{esc(kicker)}</p>'
        f'<p class="pagenum" data-fit>{index + 1:02d} / {total:02d}</p></header>'
        f"{body}"
        f'<footer class="foot"><p class="foot-note" data-fit>{esc(footer)}</p>'
        f"{dots(index, total)}</footer>"
        f"</div></div></section>"
    )


def layout_kicker(layout: str) -> str:
    return {
        "agenda": "议程",
        "chapter": "章节",
        "thesis": "判断",
        "metrics": "证据",
        "comparison": "取舍",
        "cards": "结构",
        "roadmap": "路径",
        "summary": "收束",
        "close": "决定",
    }.get(layout, "汇报")


def dots(current, total) -> str:
    buttons = []
    for i in range(total):
        current_attr = ' aria-current="true"' if i == current else ""
        buttons.append(
            f'<button type="button" class="dot" data-go="{i}" aria-label="第{i + 1}页"{current_attr}></button>'
        )
    return f'<div class="dots">{"".join(buttons)}</div>'


def title_block(lines) -> str:
    inner = "".join(f'<span class="title-line">{esc(line)}</span>' for line in lines)
    return f'<h1 class="title" data-fit>{inner}</h1>'


def render_cover(slide) -> str:
    return (
        f'<div class="body">{title_block(slide["title_lines"])}'
        f'<p class="lede" data-fit>{esc(slide["subtitle"])}</p>'
        f'<p class="aside" data-fit>{esc(slide["meta"])}</p></div>'
        f'<p class="callout" data-fit>{esc(slide["callout"])}</p>'
    )


def render_agenda(slide) -> str:
    items = []
    for item in slide["items"]:
        items.append(
            "<li data-fit>"
            f'<span class="idx">{esc(item["index"])}</span>'
            "<span>"
            f'<span class="item-title">{esc(item["title"])}</span>'
            f'<span class="item-body">{esc(item["summary"])}</span>'
            "</span></li>"
        )
    return f'<div class="body">{title_block(slide["title_lines"])}<ol class="agenda-list">{"".join(items)}</ol></div>'


def render_chapter(slide) -> str:
    aside = f'<p class="aside" data-fit>{esc(slide["aside"])}</p>' if slide.get("aside") else ""
    return (
        f'<div class="body"><p class="chapter-index" data-fit>{esc(slide["index"])}</p>'
        f'{title_block(slide["title_lines"])}'
        f'<p class="statement" data-fit>{esc(slide["statement"])}</p>{aside}</div>'
    )


def render_thesis(slide) -> str:
    cards = []
    for item in slide["supports"]:
        cards.append(
            "<article class=\"card\" data-fit>"
            f'<h2>{esc(item["title"])}</h2><p class="item-body">{esc(item["body"])}</p></article>'
        )
    return f'<div class="body">{title_block(slide["title_lines"])}<div class="support-row">{"".join(cards)}</div></div>'


def render_metrics(slide) -> str:
    count = " count-3" if len(slide["items"]) == 3 else ""
    cards = []
    for item in slide["items"]:
        cards.append(
            "<article class=\"metric\" data-fit>"
            f'<p class="metric-value">{esc(item["value"])}</p>'
            f'<p class="metric-label">{esc(item["label"])}</p>'
            f'<p class="metric-note">{esc(item["note"])}</p>'
            f'<div class="bar" aria-hidden="true"><span style="width:{int(item["bar"])}%"></span></div>'
            "</article>"
        )
    callout = f'<p class="callout" data-fit>{esc(slide["callout"])}</p>' if slide.get("callout") else ""
    return (
        f'<div class="body">{title_block(slide["title_lines"])}'
        f'<div class="metric-row{count}">{"".join(cards)}</div></div>{callout}'
    )


def render_comparison(slide) -> str:
    columns = []
    for side in ("left", "right"):
        block = slide[side]
        points = "".join(f"<li>{esc(point)}</li>" for point in block["points"])
        columns.append(
            f'<article class="card" data-fit><h2>{esc(block["title"])}</h2><ul>{points}</ul></article>'
        )
    return (
        f'<div class="body">{title_block(slide["title_lines"])}'
        f'<div class="split">{"".join(columns)}</div></div>'
        f'<p class="verdict" data-fit>{esc(slide["verdict"])}</p>'
    )


def render_cards(slide) -> str:
    count = " count-4" if len(slide["items"]) == 4 else ""
    cards = []
    for item in slide["items"]:
        cards.append(
            "<article class=\"card\" data-fit>"
            f'<p class="idx">{esc(item["index"])}</p>'
            f'<h2>{esc(item["title"])}</h2>'
            f'<p class="item-body">{esc(item["body"])}</p></article>'
        )
    note = f'<p class="note" data-fit>{esc(slide["note"])}</p>' if slide.get("note") else ""
    return (
        f'<div class="body">{title_block(slide["title_lines"])}'
        f'<div class="card-row{count}">{"".join(cards)}</div></div>{note}'
    )


def render_roadmap(slide) -> str:
    phases = []
    for item in slide["phases"]:
        phases.append(
            "<li data-fit>"
            f'<span class="window">{esc(item["window"])}</span>'
            f'<h2>{esc(item["title"])}</h2>'
            f'<p class="item-body">{esc(item["body"])}</p></li>'
        )
    return f'<div class="body">{title_block(slide["title_lines"])}<ol class="phases">{"".join(phases)}</ol></div>'


def render_summary(slide) -> str:
    cards = []
    for item in slide["items"]:
        cards.append(
            "<article class=\"card\" data-fit>"
            f'<h2>{esc(item["title"])}</h2><p class="item-body">{esc(item["body"])}</p></article>'
        )
    return f'<div class="body">{title_block(slide["title_lines"])}<div class="card-row">{"".join(cards)}</div></div>'


def render_close(slide) -> str:
    options = []
    for item in slide["options"]:
        options.append(
            "<article class=\"card\" data-fit>"
            f'<h2>{esc(item["title"])}</h2><p class="item-body">{esc(item["body"])}</p></article>'
        )
    note = f'<p class="note" data-fit>{esc(slide["note"])}</p>' if slide.get("note") else ""
    return (
        f'<div class="body">{title_block(slide["title_lines"])}'
        f'<p class="ask" data-fit>{esc(slide["ask"])}</p>'
        f'<div class="option-row">{"".join(options)}</div></div>{note}'
    )


def contrast_ratio(foreground: str, background: str) -> float:
    def channel(value: str):
        value = value.lstrip("#")
        rgb = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]

        def bend(channel_value):
            if channel_value <= 0.04045:
                return channel_value / 12.92
            return ((channel_value + 0.055) / 1.055) ** 2.4

        red, green, blue = (bend(item) for item in rgb)
        return 0.2126 * red + 0.7152 * green + 0.0722 * blue

    left, right = channel(foreground), channel(background)
    lighter, darker = max(left, right), min(left, right)
    return (lighter + 0.05) / (darker + 0.05)


def contrast_errors() -> list[str]:
    data = tokens()
    errors = []
    for theme_name, theme in data["themes"].items():
        for foreground, background, minimum in data["contrastPairs"]:
            if not theme[foreground].startswith("#") or not theme[background].startswith("#"):
                continue
            ratio = contrast_ratio(theme[foreground], theme[background])
            if ratio < minimum:
                errors.append(
                    f"{theme_name} {foreground}/{background} 对比度 {ratio:.2f}，低于 {minimum}"
                )
    return errors
