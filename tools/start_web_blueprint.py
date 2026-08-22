#!/usr/bin/env python3
"""Start the dependency-free local blueprint evaluator."""

from __future__ import annotations

import argparse
import errno
import http.server
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


def port_number(value: str) -> int:
    port = int(value)
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError("muss zwischen 0 und 65535 liegen")
    return port


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ HTML-Pipeline lokal starten")
    parser.add_argument("--host", default="127.0.0.1", help="Bind-Adresse (Standard: nur dieser Rechner)")
    parser.add_argument("--port", default=8043, type=port_number, help="Port; 0 wählt automatisch einen freien Port")
    parser.add_argument("--no-browser", action="store_true", help="Browser nicht automatisch öffnen")
    return parser.parse_args(argv)


def create_server(host: str, port: int) -> http.server.ThreadingHTTPServer:
    handler = lambda *values, **kwargs: http.server.SimpleHTTPRequestHandler(  # noqa: E731
        *values, directory=str(ROOT), **kwargs
    )
    try:
        return http.server.ThreadingHTTPServer((host, port), handler)
    except OSError as error:
        if error.errno == errno.EADDRINUSE:
            detail = f"Port {port} ist belegt; nutze --port 0"
        else:
            detail = f"Server kann auf {host}:{port} nicht starten: {error}"
        raise SystemExit(f"START FEHLGESCHLAGEN – {detail}") from error


def main() -> None:
    args = parse_args()
    preflight()
    server = create_server(args.host, args.port)
    port = int(server.server_address[1])
    url = f"http://{args.host}:{port}/web/"
    print("BUNKERFREQUENZ HTML-Pipeline")
    print("STATUS: BEREIT")
    print(f"ADRESSE: {url}")
    print("STOPP: Strg+C", flush=True)
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
