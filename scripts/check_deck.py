#!/usr/bin/env python3
"""Validate deck.json and the static HTML contract. No browser required."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decklib


def report(errors: list[str]) -> int:
    print("FAIL")
    for error in errors:
        print(f"- {error}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="检查汇报内容和自包含 HTML")
    parser.add_argument("deck", nargs="?")
    parser.add_argument("--html-file", help="只做静态 HTML 检查，不读取 deck.json")
    parser.add_argument("--html", help="要求该文件与 deck.json 重新渲染的结果一致")
    args = parser.parse_args()

    errors = decklib.contrast_errors()
    if args.html_file:
        page = Path(args.html_file).read_text(encoding="utf-8")
        errors.extend(decklib.lint_html(page))
        if errors:
            return report(errors)
        print(f"PASS html={args.html_file}")
        return 0

    if not args.deck:
        print("FAIL")
        print("- 需要 deck.json，或使用 --html-file")
        return 1

    deck = json.loads(Path(args.deck).read_text(encoding="utf-8"))
    errors.extend(decklib.validate(deck))
    if errors:
        return report(errors)
    page = decklib.render(deck)
    errors.extend(decklib.lint_html(page, deck))
    if args.html is not None:
        existing = Path(args.html).read_text(encoding="utf-8")
        if existing != page:
            errors.append("HTML 与 deck.json 不一致，请重新运行 render_deck.py")
    if errors:
        return report(errors)
    print(f"PASS deck={args.deck} slides={len(deck['slides'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
