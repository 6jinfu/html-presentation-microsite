#!/usr/bin/env python3
"""Regression tests for the report deck contract, renderer, and browser checks."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"
EXAMPLE = ROOT / "examples" / "lingchuan-q3" / "deck.json"
EXAMPLE_HTML = ROOT / "examples" / "lingchuan-q3" / "index.html"
sys.path.insert(0, str(SCRIPTS))

import decklib  # noqa: E402


def run(args):
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class DeckContractTest(unittest.TestCase):
    def test_example_renders_and_matches_file(self):
        deck = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        page = decklib.render(deck)
        self.assertEqual(page, EXAMPLE_HTML.read_text(encoding="utf-8"))
        self.assertNotIn("https://", page)
        self.assertNotIn("{{", page)
        self.assertEqual(page.count('data-layout="'), 12)

    def test_check_deck_command(self):
        result = run([str(SCRIPTS / "check_deck.py"), str(EXAMPLE), "--html", str(EXAMPLE_HTML)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_showcase_fixture(self):
        deck = json.loads((FIXTURES / "showcase.json").read_text(encoding="utf-8"))
        self.assertEqual(decklib.validate(deck), [])
        page = decklib.render(deck)
        self.assertEqual(decklib.lint_html(page, deck), [])
        self.assertIn('data-theme="showcase"', page)

    def test_negative_content_cases(self):
        deck = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        pptx = json.loads(json.dumps(deck))
        pptx["meta"]["formats"] = ["html", "pptx"]
        self.assertTrue(any("PPTX" in error for error in decklib.validate(pptx)))

        short = json.loads(json.dumps(deck))
        short["meta"]["mode"] = "showcase"
        self.assertTrue(any("showcase" in error for error in decklib.validate(short)))

        placeholder = json.loads(json.dumps(deck))
        placeholder["slides"][0]["title_lines"] = ["{{标题}}"]
        self.assertTrue(any("占位" in error for error in decklib.validate(placeholder)))

        long_title = json.loads(json.dumps(deck))
        long_title["slides"][4]["title_lines"] = ["这是一个明显超过十八字的业务标题句子啊"]
        self.assertTrue(any("超过" in error for error in decklib.validate(long_title)))

        missing_gap = json.loads(json.dumps(deck))
        missing_gap["meta"]["gaps"] = ["这里没有写进任何一页"]
        page = decklib.render(deck)
        self.assertTrue(any("缺口" in error for error in decklib.lint_html(page, missing_gap)))

    def test_static_html_fixtures(self):
        remote = run([str(SCRIPTS / "check_deck.py"), "--html-file", str(FIXTURES / "remote.html")])
        self.assertEqual(remote.returncode, 1, remote.stdout)
        self.assertIn("外部地址", remote.stdout)
        placeholder = run([str(SCRIPTS / "check_deck.py"), "--html-file", str(FIXTURES / "placeholder.html")])
        self.assertEqual(placeholder.returncode, 1)
        self.assertIn("占位符", placeholder.stdout)

    def test_contrast_and_layout_registry(self):
        self.assertEqual(decklib.contrast_errors(), [])
        spec = decklib.schema()
        rendered = {
            "cover", "agenda", "chapter", "thesis", "metrics",
            "comparison", "cards", "roadmap", "summary", "close",
        }
        self.assertEqual(set(spec["layouts"]), rendered)

    def test_existing_skill_contract(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        prompt = (ROOT / "references" / "prompt-template.md").read_text(encoding="utf-8")
        outline = (ROOT / "references" / "slide-outline-template.md").read_text(encoding="utf-8")
        self.assertIn('name: "html-presentation-microsite"', skill)
        self.assertIn("Showcase mode", skill)
        self.assertIn("Report mode", skill)
        self.assertIn("self-contained HTML", prompt)
        self.assertIn("10-15", outline)


class BrowserCheckTest(unittest.TestCase):
    def test_layout_and_pdf(self):
        chrome = __import__("chrome_cdp").find_chrome()
        if not chrome:
            self.skipTest("未找到 Chrome，版式和 PDF 未验证")
        layout = run([str(SCRIPTS / "check_layout.py"), str(EXAMPLE_HTML)])
        self.assertEqual(layout.returncode, 0, layout.stdout + layout.stderr)
        showcase = json.loads((FIXTURES / "showcase.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            showcase_html = Path(directory) / "showcase.html"
            showcase_html.write_text(decklib.render(showcase), encoding="utf-8")
            dark = run([str(SCRIPTS / "check_layout.py"), str(showcase_html)])
            self.assertEqual(dark.returncode, 0, dark.stdout + dark.stderr)
        for fixture, marker in (
            ("overflow.html", "overflow"),
            ("overlap.html", "overlap"),
            ("blank.html", "blank"),
        ):
            result = run([str(SCRIPTS / "check_layout.py"), str(FIXTURES / fixture)])
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn(marker, result.stdout)
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "lingchuan.pdf"
            exported = run([
                str(SCRIPTS / "export_pdf.py"),
                str(EXAMPLE_HTML),
                "-o",
                str(pdf),
                "--expect-slides",
                "12",
            ])
            self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)
            self.assertTrue(pdf.exists())
            self.assertGreater(pdf.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
