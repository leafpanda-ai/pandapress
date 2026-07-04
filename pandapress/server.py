"""PandaPress 实时预览服务器."""
import os
import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path


def serve(output_dir: str, port: int = 8080):
    directory = Path(output_dir).resolve()
    os.chdir(directory)

    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"PandaPress preview: {url}")
        threading.Thread(target=lambda: webbrowser.open(url), daemon=True).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
