#!/usr/bin/env python3
"""Print a deck to a 16:9 PDF with Chrome. This is not an editable PPTX export."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import chrome_cdp


def page_boxes(data: bytes) -> list[tuple[float, float]]:
    boxes = []
    for match in re.finditer(rb"/MediaBox\s*\[\s*([^\]]+)\]", data):
        numbers = [float(item) for item in match.group(1).split()]
        if len(numbers) == 4:
            boxes.append((numbers[2] - numbers[0], numbers[3] - numbers[1]))
    return boxes


def page_count(data: bytes) -> int:
    return len(re.findall(rb"/Type\s*/Page\b", data))


def stop(process: subprocess.Popen):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()


def wait_for_pdf(path: Path, process: subprocess.Popen, timeout: float = 30) -> bytes:
    """Chrome writes the PDF and then often keeps running. Stop it after %%EOF."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if path.exists() and path.stat().st_size > 1000:
            data = path.read_bytes()
            if data.startswith(b"%PDF") and data.rstrip().endswith(b"%%EOF"):
                stop(process)
                return data
        if process.poll() is not None:
            return path.read_bytes() if path.exists() else b""
        time.sleep(0.25)
    stop(process)
    return path.read_bytes() if path.exists() else b""


def main() -> int:
    parser = argparse.ArgumentParser(description="用 Chrome 把 HTML 汇报打印成 16:9 PDF")
    parser.add_argument("html")
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--expect-slides", type=int)
    args = parser.parse_args()
    chrome = chrome_cdp.find_chrome()
    if not chrome:
        print("UNAVAILABLE 未找到 Chrome，PDF 未生成，不能声明已支持 PDF")
        return 2
    source = Path(args.html).resolve()
    destination = Path(args.output).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="deck-pdf-"))
    command = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-pdf-header-footer",
        "--hide-scrollbars",
        f"--user-data-dir={profile}",
        f"--print-to-pdf={destination}",
        source.as_uri(),
    ]
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    data = wait_for_pdf(destination, process)
    shutil.rmtree(profile, ignore_errors=True)
    if not data.startswith(b"%PDF"):
        print("FAIL PDF 没有生成")
        return 1
    count = page_count(data)
    boxes = page_boxes(data)
    problems = []
    if args.expect_slides is not None and count != args.expect_slides:
        problems.append(f"PDF 页数 {count}，幻灯片数 {args.expect_slides}")
    if not boxes:
        problems.append("PDF 里没有读到 MediaBox，页面尺寸未验证")
    else:
        width, height = boxes[0]
        if abs(width - 960) > 6 or abs(height - 540) > 6:
            problems.append(f"页面尺寸是 {width:.1f}×{height:.1f} pt，不是 16:9 的 960×540 pt")
        if any(abs(box[0] - width) > 2 or abs(box[1] - height) > 2 for box in boxes):
            problems.append("PDF 各页尺寸不一致")
    if problems:
        print("FAIL")
        for problem in problems:
            print(f"- {problem}")
        print(f"pdf={destination}")
        return 1
    size = f"{boxes[0][0]:.1f}x{boxes[0][1]:.1f}pt" if boxes else "size-unread"
    print(f"PASS pdf={destination} pages={count} size={size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
