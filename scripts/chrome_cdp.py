#!/usr/bin/env python3
"""Small Chrome DevTools client used by layout and PDF checks."""

from __future__ import annotations

import base64
import json
import os
import shutil
import socket
import struct
import subprocess
import time
import urllib.request
from pathlib import Path


def find_chrome() -> str | None:
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    return None


class ChromeError(RuntimeError):
    pass


class Chrome:
    def __init__(self, chrome_path: str):
        self.chrome_path = chrome_path
        self.proc = None
        self.sock = None
        self.mid = 0
        self.profile = None
        self.port = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def start(self):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            self.port = probe.getsockname()[1]
        self.profile = Path(f"/tmp/deck-chrome-{os.getpid()}-{self.port}")
        self.proc = subprocess.Popen(
            [
                self.chrome_path,
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-extensions",
                "--allow-file-access-from-files",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                f"--remote-debugging-port={self.port}",
                f"--user-data-dir={self.profile}",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        pages = self._wait_pages()
        page = next(item for item in pages if item.get("type") == "page")
        self._connect(page["webSocketDebuggerUrl"])
        self.call("Page.enable")
        self.call("Runtime.enable")

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None
        if self.proc is not None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            self.proc = None
        if self.profile and self.profile.exists():
            shutil.rmtree(self.profile, ignore_errors=True)

    def open(self, path: Path):
        target = path.resolve().as_uri()
        self.call("Page.navigate", {"url": target})
        self.call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 1920, "height": 1080, "deviceScaleFactor": 1, "mobile": False},
        )
        deadline = time.time() + 15
        while time.time() < deadline:
            state = self.evaluate("document.readyState")
            ready = self.evaluate("!!document.querySelector('.slide')")
            if state == "complete" and ready:
                self.evaluate("window.dispatchEvent(new Event('resize'))")
                return
            time.sleep(0.1)
        raise ChromeError(f"页面没有在时限内打开：{path}")

    def evaluate(self, expression: str, await_promise: bool = False):
        result = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": await_promise,
            },
        )
        if "exceptionDetails" in result:
            detail = result["exceptionDetails"]
            text = detail.get("text") or detail.get("exception", {}).get("description")
            raise ChromeError(text or "页面脚本执行失败")
        return result.get("result", {}).get("value")

    def screenshot(self, destination: Path):
        payload = self.call("Page.captureScreenshot", {"format": "png"})
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(base64.b64decode(payload["data"]))

    def call(self, method: str, params: dict | None = None, timeout: float = 20):
        self.mid += 1
        message_id = self.mid
        self._send({"id": message_id, "method": method, "params": params or {}})
        deadline = time.time() + timeout
        while time.time() < deadline:
            message = self._recv()
            if message.get("id") == message_id:
                if "error" in message:
                    raise ChromeError(f"{method}: {message['error']}")
                return message.get("result", {})
        raise ChromeError(f"{method} 超时")

    def _wait_pages(self):
        deadline = time.time() + 15
        url = f"http://127.0.0.1:{self.port}/json/list"
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise ChromeError("Chrome 在打开调试端口前退出")
            try:
                with urllib.request.urlopen(url, timeout=1) as response:
                    pages = json.loads(response.read().decode())
                if pages:
                    return pages
            except OSError:
                time.sleep(0.15)
        raise ChromeError("无法连接 Chrome 调试端口")

    def _connect(self, ws_url: str):
        host_path = ws_url.split("://", 1)[1]
        host_port, path = host_path.split("/", 1)
        host, port = host_port.split(":")
        sock = socket.create_connection((host, int(port)), timeout=10)
        key = base64.b64encode(os.urandom(16)).decode()
        request = (
            f"GET /{path} HTTP/1.1\r\n"
            f"Host: {host_port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        sock.sendall(request.encode())
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = sock.recv(4096)
            if not chunk:
                raise ChromeError("Chrome WebSocket 握手失败")
            response += chunk
        if b" 101 " not in response.split(b"\r\n", 1)[0]:
            raise ChromeError(response.decode(errors="replace"))
        sock.settimeout(20)
        self.sock = sock

    def _send(self, payload: dict):
        data = json.dumps(payload).encode()
        mask = os.urandom(4)
        header = bytearray([0x81])
        length = len(data)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header += struct.pack("!H", length)
        else:
            header.append(0x80 | 127)
            header += struct.pack("!Q", length)
        header += mask
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(data))
        self.sock.sendall(header + masked)

    def _recv(self) -> dict:
        chunks = []
        while True:
            opcode, fin, data = self._frame()
            if opcode == 8:
                raise ChromeError("Chrome 关闭了连接")
            if opcode == 9:
                self._pong(data)
                continue
            if opcode in (0, 1):
                chunks.append(data)
                if fin:
                    return json.loads(b"".join(chunks).decode())

    def _pong(self, data: bytes):
        mask = os.urandom(4)
        frame = bytearray([0x8A, 0x80 | len(data)])
        frame += mask
        frame += bytes(byte ^ mask[index % 4] for index, byte in enumerate(data))
        self.sock.sendall(frame)

    def _frame(self):
        first, second = self._exact(2)
        fin = bool(first & 0x80)
        opcode = first & 0x0F
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", self._exact(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self._exact(8))[0]
        if second & 0x80:
            mask = self._exact(4)
            payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(self._exact(length)))
        else:
            payload = self._exact(length)
        return opcode, fin, payload

    def _exact(self, size: int) -> bytes:
        chunks = []
        remaining = size
        while remaining:
            try:
                chunk = self.sock.recv(remaining)
            except socket.timeout as error:
                raise ChromeError("读取 Chrome 响应超时") from error
            if not chunk:
                raise ChromeError("Chrome 连接中断")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)
