#!/usr/bin/env python3
"""Render deck.json into one self-contained HTML presentation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decklib


def main() -> int:
    parser = argparse.ArgumentParser(description="把 deck.json 渲染成自包含 HTML 汇报")
    parser.add_argument("deck")
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    deck = json.loads(Path(args.deck).read_text(encoding="utf-8"))
    try:
        page = decklib.render(deck)
    except ValueError as error:
        print("FAIL", file=sys.stderr)
        print(error, file=sys.stderr)
        return 1
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page, encoding="utf-8")
    print(f"PASS html={destination} slides={len(deck['slides'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
