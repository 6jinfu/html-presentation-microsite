#!/usr/bin/env python3
"""Open a deck in Chrome and check overflow, overlap, blank slides, and font ink."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import chrome_cdp

MEASURE = r"""
(() => {
  const slides = [...document.querySelectorAll('.slide')];
  const issues = [];
  function boxes(canvas) {
    return [...canvas.querySelectorAll('[data-fit]')].map((node) => {
      const rect = node.getBoundingClientRect();
      return {node, rect};
    });
  }
  slides.forEach((slide, index) => {
    slides.forEach((other) => { other.hidden = true; other.classList.remove('is-active'); });
    slide.hidden = false;
    slide.classList.add('is-active');
    const canvas = slide.querySelector('.slide-canvas') || slide;
    const canvasRect = canvas.getBoundingClientRect();
    const text = (canvas.innerText || '').replace(/\s+/g, '');
    const layout = slide.getAttribute('data-layout') || '';
    const id = slide.getAttribute('data-id') || String(index + 1);
    if (text.length < 12) issues.push({slide: id, type: 'blank', detail: '可见文字少于 12 个字'});
    boxes(canvas).forEach(({node, rect}) => {
      const overflow = node.scrollWidth > node.clientWidth + 1 || node.scrollHeight > node.clientHeight + 1;
      if (overflow) {
        issues.push({slide: id, type: 'overflow', detail: node.className || node.tagName});
      }
      const outside = rect.left < canvasRect.left - 1 || rect.top < canvasRect.top - 1
        || rect.right > canvasRect.right + 1 || rect.bottom > canvasRect.bottom + 1;
      if (outside) issues.push({slide: id, type: 'outside', detail: node.className || node.tagName});
    });
    const fitted = boxes(canvas);
    for (let i = 0; i < fitted.length; i += 1) {
      for (let j = i + 1; j < fitted.length; j += 1) {
        const a = fitted[i];
        const b = fitted[j];
        if (a.node.contains(b.node) || b.node.contains(a.node)) continue;
        const x = Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.left, b.rect.left);
        const y = Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.top, b.rect.top);
        if (x > 4 && y > 4) {
          issues.push({slide: id, type: 'overlap', detail: (a.node.className || a.node.tagName) + ' / ' + (b.node.className || b.node.tagName)});
        }
      }
    }
    const roomy = ['cover', 'chapter', 'close'];
    if (!roomy.includes(layout)) {
      const body = canvas.querySelector('.body');
      const content = body ? [...body.querySelectorAll('[data-fit]')] : [];
      const height = content.reduce((sum, node) => sum + node.getBoundingClientRect().height, 0);
      if (height < 280) issues.push({slide: id, type: 'sparse', detail: '内容区高度 ' + Math.round(height) + 'px'});
    }
  });
  slides.forEach((other, index) => {
    other.hidden = index !== 0;
    other.classList.toggle('is-active', index === 0);
  });
  return issues;
})()
"""


def show(browser, number: int):
    browser.evaluate(
        f"location.hash = '#{number}'; window.dispatchEvent(new HashChangeEvent('hashchange'));"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="用 Chrome 检查幻灯片溢出、重叠、空白和字体")
    parser.add_argument("html")
    parser.add_argument("--screenshot-dir")
    args = parser.parse_args()
    chrome = chrome_cdp.find_chrome()
    if not chrome:
        print("UNAVAILABLE 未找到 Chrome，不能把静态检查当成版式通过")
        return 2
    path = Path(args.html)
    try:
        with chrome_cdp.Chrome(chrome) as browser:
            browser.open(path)
            browser.evaluate("document.documentElement.classList.add('is-measuring')")
            font = browser.evaluate(
                """
                (async () => {
                  await document.fonts.ready;
                  const node = document.querySelector('.title-line') || document.body;
                  const style = getComputedStyle(node);
                  const canvas = document.createElement('canvas');
                  canvas.width = 96; canvas.height = 96;
                  const ctx = canvas.getContext('2d');
                  ctx.font = style.font;
                  ctx.fillStyle = '#000';
                  ctx.fillText('汇报', 4, 72);
                  const pixels = ctx.getImageData(0, 0, 96, 96).data;
                  let ink = 0;
                  for (let i = 3; i < pixels.length; i += 4) if (pixels[i] > 16) ink += 1;
                  return {font: style.fontFamily, ink};
                })()
                """,
                await_promise=True,
            )
            issues = browser.evaluate(MEASURE) or []
            has_nav = browser.evaluate("!!document.querySelector('.dot')")
            if has_nav:
                show(browser, 2)
                moved = browser.evaluate(
                    "[...document.querySelectorAll('.slide')].findIndex((slide) => slide.classList.contains('is-active'))"
                )
                ended = browser.evaluate(
                    """
                    window.dispatchEvent(new KeyboardEvent('keydown', {key: 'End'}));
                    [...document.querySelectorAll('.slide')].findIndex((slide) => slide.classList.contains('is-active'))
                    """
                )
                last = browser.evaluate("document.querySelectorAll('.slide').length - 1")
                browser.evaluate("window.dispatchEvent(new KeyboardEvent('keydown', {key: 'Home'}));")
                if moved != 1:
                    issues.append({"slide": "document", "type": "navigation", "detail": f"链接到第 2 页后停在 {moved}"})
                if ended != last:
                    issues.append({"slide": "document", "type": "navigation", "detail": "End 没有到达最后一页"})
            if not font or font.get("ink", 0) < 30:
                issues.append({"slide": "document", "type": "font", "detail": f"中文没有画出来：{font}"})
            shots = []
            if args.screenshot_dir:
                directory = Path(args.screenshot_dir)
                total = browser.evaluate("document.querySelectorAll('.slide').length")
                for number in range(1, total + 1):
                    show(browser, number)
                    slide_id = browser.evaluate(
                        "[...document.querySelectorAll('.slide')].find((slide) => slide.classList.contains('is-active')).dataset.id"
                    )
                    destination = directory / f"{number:02d}-{slide_id}.png"
                    browser.screenshot(destination)
                    shots.append(str(destination))
    except chrome_cdp.ChromeError as error:
        print("UNAVAILABLE " + str(error))
        return 2
    if issues:
        print("FAIL")
        for issue in issues:
            print(f"- {issue['slide']} {issue['type']}: {issue['detail']}")
        return 1
    print(f"PASS layout={path} font_ink={font['ink']} screenshots={len(shots)}")
    if shots:
        print(json.dumps(shots, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
