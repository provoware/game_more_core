#!/usr/bin/env python3
"""Start the dependency-free local writing A4 alpha client."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime
import errno
from functools import partial
import http.server
import json
from pathlib import Path
import sys
import tempfile
import threading
import uuid
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
A4_STATIC = ROOT / "web" / "a4"
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bunkerfrequenz.application.game_client_session import GameClientSession  # noqa: E402
from bunkerfrequenz.application.game_recovery import GameRecoveryService  # noqa: E402
from bunkerfrequenz.application.incident_service import build_incident_catalog  # noqa: E402
from bunkerfrequenz.domain.character import CharacterState  # noqa: E402
from bunkerfrequenz.infrastructure.persistence import (  # noqa: E402
    JournalContext,
    PersistenceError,
    PersistenceKernel,
)
from bunkerfrequenz.presentation.a4_game_projection import build_a4_game_projection  # noqa: E402

MAX_BODY_BYTES = 64 * 1024
REQUIRED = (
    "web/a4/index.html",
    "web/a4/styles.css",
    "web/a4/app.js",
    "web/a4/starter.json",
    "manifests/JOURNAL_MANIFEST.json",
    "manifests/INCIDENT_MANIFEST.json",
)


def _load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"START FEHLGESCHLAGEN – ungültige JSON-Datei: {path}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"START FEHLGESCHLAGEN – JSON-Wurzel muss Objekt sein: {path}")
    return value


def preflight(root: Path = ROOT) -> None:
    missing = [path for path in REQUIRED if not (root / path).is_file()]
    if missing:
        raise SystemExit("START FEHLGESCHLAGEN – fehlt: " + ", ".join(missing))


def _prepare_save_dir(save_dir: Path) -> Path:
    resolved = save_dir.expanduser().resolve()
    try:
        resolved.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix=".a4-write-probe-", dir=resolved):
            pass
    except OSError as exc:
        raise SystemExit(
            "START FEHLGESCHLAGEN – Spielstandordner ist nicht beschreibbar: "
            f"{resolved} ({exc})"
        ) from exc
    return resolved


def port_number(value: str) -> int:
    port = int(value)
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError("muss zwischen 0 und 65535 liegen")
    return port


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ A4 Game Client lokal starten")
    parser.add_argument("--port", default=8044, type=port_number, help="Port; 0 wählt automatisch einen freien Port")
    parser.add_argument(
        "--save-dir",
        type=Path,
        default=Path.home() / ".local" / "share" / "bunkerfrequenz" / "a4-alpha",
        help="Lokaler Spielstandordner",
    )
    parser.add_argument("--no-browser", action="store_true", help="Browser nicht automatisch öffnen")
    return parser.parse_args(argv)


class A4ClientRuntime:
    def __init__(self, save_dir: Path) -> None:
        journal_manifest = _load_json(ROOT / "manifests" / "JOURNAL_MANIFEST.json")
        incident_manifest = _load_json(ROOT / "manifests" / "INCIDENT_MANIFEST.json")
        allowed = set(journal_manifest.get("event_types", ()))
        if not allowed:
            raise SystemExit("START FEHLGESCHLAGEN – JOURNAL_MANIFEST besitzt keine Eventtypen")
        self.game_version = str(journal_manifest.get("version", "0.8.3-c1"))
        self.incident_catalog = build_incident_catalog(incident_manifest)
        self.session_id = f"a4-{uuid.uuid4()}"
        self.save_dir = _prepare_save_dir(save_dir)
        self.startup_recovery = None
        try:
            self.kernel = PersistenceKernel(self.save_dir, allowed)
        except PersistenceError as exc:
            try:
                self.kernel = PersistenceKernel.open_for_recovery(self.save_dir, allowed)
                recovery_context = JournalContext(
                    datetime.now().astimezone().isoformat(timespec="seconds"),
                    self.session_id,
                    "player-local",
                    "system",
                    "local-save",
                    f"startup-recovery:{uuid.uuid4()}",
                    "a4-local-client-recovery",
                    self.game_version,
                    None,
                )
                self.startup_recovery = GameRecoveryService(self.kernel).recover(
                    context=recovery_context
                )
            except (PersistenceError, ValueError, OSError) as recovery_exc:
                raise SystemExit(
                    "START FEHLGESCHLAGEN – Spielstand benötigt Recovery, "
                    f"konnte aber nicht sicher wiederhergestellt werden: {recovery_exc}"
                ) from exc
        except OSError as exc:
            raise SystemExit(
                "START FEHLGESCHLAGEN – Spielstand konnte nicht sicher geöffnet werden: "
                f"{self.save_dir} ({exc})"
            ) from exc
        self.session = GameClientSession(
            self.kernel,
            incident_catalog=self.incident_catalog,
            incident_contract_version=incident_manifest["version"],
        )
        self.starter = _load_json(ROOT / "web" / "a4" / "starter.json")
        self.lock = threading.RLock()

    def projection(self) -> dict:
        with self.lock:
            return build_a4_game_projection(
                self.session.read_state(),
                incident_catalog=self.incident_catalog,
            )

    def _context(
        self,
        command_id: str,
        entity_type: str,
        entity_id: str,
        character_id: str | None,
    ) -> JournalContext:
        return JournalContext(
            datetime.now().astimezone().isoformat(timespec="seconds"),
            self.session_id,
            character_id or "player-local",
            entity_type,
            entity_id,
            command_id,
            "a4-local-client",
            self.game_version,
            character_id,
        )

    def bootstrap(self, request: dict) -> dict:
        with self.lock:
            bootstrap_id = request.get("command_id")
            if not isinstance(bootstrap_id, str) or not bootstrap_id.strip():
                return {"status": "rejected", "error_code": "invalid_command_id"}

            starter = deepcopy(self.starter)
            character_raw = starter.get("character")
            event_raw = starter.get("event")
            economy_raw = starter.get("economy")
            if not all(isinstance(item, dict) for item in (character_raw, event_raw, economy_raw)):
                return {"status": "rejected", "error_code": "starter_invalid"}

            character_name = request.get("character_name")
            event_name = request.get("event_name")
            if isinstance(character_name, str) and character_name.strip():
                character_raw["display_name"] = character_name.strip()
            if isinstance(event_name, str) and event_name.strip():
                event_raw["display_name"] = event_name.strip()

            event_id = event_raw.get("event_id")
            if not isinstance(event_id, str) or not event_id:
                return {"status": "rejected", "error_code": "starter_event_id_invalid"}

            try:
                character = CharacterState.from_dict(character_raw)
                current = self.session.read_state()
                if "event" in current:
                    existing_event = current.get("event")
                    if existing_event != event_raw:
                        return {"status": "rejected", "error_code": "save_exists", "state": self.projection()}
                if "economy" in current:
                    existing_economy = current.get("economy")
                    if existing_economy != economy_raw:
                        return {"status": "rejected", "error_code": "save_exists", "state": self.projection()}
                if "event" in current and "economy" in current:
                    return {"status": "rejected", "error_code": "save_exists", "state": self.projection()}
                self.session.bootstrap_character(character)
            except (ValueError, RuntimeError) as exc:
                return {"status": "rejected", "error_code": "bootstrap_character_failed", "detail": str(exc)}

            state_after_character = self.session.read_state()
            if "event" not in state_after_character:
                create_command = {
                    "type": "event.create",
                    "command_id": f"{bootstrap_id}:event",
                    "event": event_raw,
                }
                create_result = self.session.dispatch(
                    create_command,
                    context=self._context(
                        create_command["command_id"], "event", event_id, character.character_id
                    ),
                )
                if create_result.status != "confirmed":
                    return self._command_payload(create_result)

            state_after_event = self.session.read_state()
            if "economy" not in state_after_event:
                economy_command = {
                    "type": "economy.initialize",
                    "command_id": f"{bootstrap_id}:economy",
                    "economy": economy_raw,
                }
                economy_result = self.session.dispatch(
                    economy_command,
                    context=self._context(
                        economy_command["command_id"], "event", event_id, character.character_id
                    ),
                )
                return self._command_payload(economy_result)

            return {"status": "confirmed", "state": self.projection(), "committed_event_ids": []}

    def command(self, command: dict) -> dict:
        with self.lock:
            state = self.session.read_state()
            character = state.get("character")
            command_id = command.get("command_id")
            if not isinstance(command_id, str) or not command_id.strip():
                return {"status": "rejected", "error_code": "invalid_command_id", "state": self.projection()}
            if not isinstance(character, dict):
                return {"status": "rejected", "error_code": "character_missing", "state": self.projection()}
            character_id = character.get("character_id")
            if not isinstance(character_id, str) or not character_id:
                return {"status": "rejected", "error_code": "character_missing", "state": self.projection()}

            if command.get("type") == "profile.update":
                context = self._context(command_id, "character", character_id, character_id)
            else:
                event = state.get("event")
                if not isinstance(event, dict):
                    return {"status": "rejected", "error_code": "event_missing", "state": self.projection()}
                event_id = event.get("event_id")
                if not isinstance(event_id, str) or not event_id:
                    return {"status": "rejected", "error_code": "event_missing", "state": self.projection()}
                context = self._context(command_id, "event", event_id, character_id)

            result = self.session.dispatch(command, context=context)
            return self._command_payload(result)

    def checkpoint(self) -> dict:
        with self.lock:
            try:
                snapshot_id = self.session.create_checkpoint()
            except (ValueError, RuntimeError) as exc:
                return {"status": "rejected", "error_code": "checkpoint_failed", "detail": str(exc)}
            return {"status": "confirmed", "snapshot_id": snapshot_id, "state": self.projection()}

    def _command_payload(self, result) -> dict:
        payload = {
            "status": result.status,
            "committed_event_ids": list(result.committed_event_ids),
            "idempotent_replay": result.idempotent_replay,
            "error_code": result.error_code,
            "state": self.projection(),
        }
        if result.error_detail:
            payload["detail"] = result.error_detail
        return payload


class A4RequestHandler(http.server.SimpleHTTPRequestHandler):
    server_version = "BunkerfrequenzA4/0.8.5-b1"

    @property
    def runtime(self) -> A4ClientRuntime:
        return self.server.runtime  # type: ignore[attr-defined]

    def _json(self, status: int, payload: dict) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(encoded)

    def _origin_allowed(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True
        port = int(self.server.server_address[1])
        return origin in {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}

    def _body(self) -> dict | None:
        if not self._origin_allowed():
            self._json(403, {"status": "rejected", "error_code": "origin_forbidden"})
            return None
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            self._json(415, {"status": "rejected", "error_code": "json_required"})
            return None
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 2 or length > MAX_BODY_BYTES:
            self._json(413, {"status": "rejected", "error_code": "body_size_invalid"})
            return None
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(400, {"status": "rejected", "error_code": "invalid_json"})
            return None
        if not isinstance(payload, dict):
            self._json(400, {"status": "rejected", "error_code": "json_object_required"})
            return None
        return payload

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/health":
            recovery = self.runtime.startup_recovery
            self._json(200, {
                "status": "ready",
                "save_dir": str(self.runtime.save_dir),
                "startup_recovery": None if recovery is None else recovery.status,
            })
            return
        if self.path == "/api/state":
            self._json(200, {"status": "confirmed", "state": self.runtime.projection()})
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        payload = self._body()
        if payload is None:
            return
        if self.path == "/api/new-game":
            result = self.runtime.bootstrap(payload)
        elif self.path == "/api/command":
            result = self.runtime.command(payload)
        elif self.path == "/api/checkpoint":
            result = self.runtime.checkpoint()
        else:
            self._json(404, {"status": "rejected", "error_code": "route_not_found"})
            return
        self._json(200 if result.get("status") == "confirmed" else 422, result)

    def log_message(self, format: str, *args) -> None:
        super().log_message(format, *args)


def create_server(port: int, runtime: A4ClientRuntime) -> http.server.ThreadingHTTPServer:
    handler = partial(A4RequestHandler, directory=str(A4_STATIC))
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError as exc:
        if exc.errno == errno.EADDRINUSE:
            detail = f"Port {port} ist belegt; nutze --port 0 für automatische freie Portwahl"
        else:
            detail = f"lokaler Server konnte auf Port {port} nicht gestartet werden: {exc}"
        raise SystemExit(f"START FEHLGESCHLAGEN – {detail}") from exc
    server.runtime = runtime  # type: ignore[attr-defined]
    return server


def main() -> None:
    args = parse_args()
    preflight()
    runtime = A4ClientRuntime(args.save_dir)
    server = create_server(args.port, runtime)
    port = int(server.server_address[1])
    url = f"http://127.0.0.1:{port}/"
    print("BUNKERFREQUENZ A4 GAME CLIENT")
    print("STATUS: BEREIT")
    print(f"SPIELSTAND: {runtime.save_dir}")
    print(f"ADRESSE: {url}")
    if runtime.startup_recovery is not None:
        print(f"RECOVERY: {runtime.startup_recovery.status.upper()}")
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
