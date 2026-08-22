#!/usr/bin/env python3
"""Start the dependency-free local blueprint evaluator."""

from __future__ import annotations

import argparse
import http.server
import socket
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "web/index.html",
    "web/styles.css",
    "web/app.js",
    "manifests/UI_MANIFEST.json",
    "content/de/ui/character_forge.json",
    "docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp",
)


def preflight() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("START FEHLGESCHLAGEN – fehlt: " + ", ".join(missing))


def find_port(host: str, requested: int) -> int:
    with socket.socket() as probe:
        probe.bind((host, requested))
        return int(probe.getsockname()[1])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ HTML-Pipeline lokal starten")
    parser.add_argument("--host", default="127.0.0.1", help="Bind-Adresse (Standard: nur dieser Rechner)")
    parser.add_argument("--port", default=8043, type=int, help="Port; 0 wählt automatisch einen freien Port")
    parser.add_argument("--no-browser", action="store_true", help="Browser nicht automatisch öffnen")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    preflight()
    try:
        port = find_port(args.host, args.port)
    except OSError as error:
        raise SystemExit(f"START FEHLGESCHLAGEN – Port {args.port} ist belegt: {error}") from error
    handler = lambda *values, **kwargs: http.server.SimpleHTTPRequestHandler(  # noqa: E731
        *values, directory=str(ROOT), **kwargs
    )
    server = http.server.ThreadingHTTPServer((args.host, port), handler)
    url = f"http://{args.host}:{port}/web/"
    print("BUNKERFREQUENZ HTML-Pipeline")
    print("STATUS: BEREIT")
    print(f"ADRESSE: {url}")
    print("STOPP: Strg+C")
    if not args.no_browser:
        threading.Timer(0.25, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSTATUS: BEENDET")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
