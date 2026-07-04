"""PandaPress 实时预览服务器 + 文件变更监听."""
import os
import sys
import time
import http.server
import socketserver
import threading
from pathlib import Path
from typing import Callable, Optional


def serve(
    output_dir: str,
    port: int = 8080,
    input_dir: Optional[str] = None,
    rebuild: Optional[Callable[[], None]] = None,
):
    """Start a preview server and optionally watch for changes."""
    directory = Path(output_dir).resolve()
    os.chdir(directory)

    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"PandaPress preview: {url}")

        # Start file watcher in background if input_dir and rebuild provided
        if input_dir is not None and rebuild is not None:
            watcher = _start_watcher(Path(input_dir), rebuild)
        else:
            watcher = None

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
        finally:
            if watcher is not None:
                watcher.stop()


def _start_watcher(src: Path, rebuild: Callable[[], None]) -> "_Watcher":
    """Start a background file watcher thread."""
    w = _Watcher(src, rebuild)
    w.start()
    return w


class _Watcher:
    """Simple file watcher that polls mtime every second."""

    def __init__(self, src: Path, rebuild: Callable[[], None]):
        self._src = src
        self._rebuild = rebuild
        self._snapshot: dict = {}
        self._stop_event = threading.Event()

    def start(self):
        self._scan()
        t = threading.Thread(target=self._loop, daemon=True, name="pandapress-watcher")
        t.start()

    def stop(self):
        self._stop_event.set()

    def _scan(self) -> dict:
        snap = {}
        for f in self._src.rglob("*"):
            if f.is_file() and f.suffix in (".md", ".css", ".html"):
                try:
                    snap[str(f.relative_to(self._src))] = f.stat().st_mtime_ns
                except OSError:
                    pass
        return snap

    def _loop(self):
        while not self._stop_event.is_set():
            time.sleep(1)
            snap = self._scan()
            if snap != self._snapshot:
                changed = set(snap.keys()) - set(self._snapshot.keys())
                changed |= {k for k in self._snapshot if snap.get(k) != self._snapshot[k]}
                for c in sorted(changed):
                    print(f"  🔄 changed: {c}")
                self._snapshot = snap
                try:
                    self._rebuild()
                except Exception as e:
                    print(f"  ❌ rebuild error: {e}")
