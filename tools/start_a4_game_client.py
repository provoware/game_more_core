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

from bunkerfrequenz.application.assistant_game_client_session import AssistantGameClientSession  # noqa: E402
from bunkerfrequenz.application.game_recovery import GameRecoveryService  # noqa: E402
from bunkerfrequenz.application.incident_service import build_incident_catalog  # noqa: E402
from bunkerfrequenz.domain.character import CharacterState  # noqa: E402
from bunkerfrequenz.infrastructure.persistence import (  # noqa: E402
    JournalContext,
    PersistenceError,
    PersistenceKernel,
)
from bunkerfrequenz.presentation.a4_game_projection import build_a4_game_projection  # noqa: E402
from bunkerfrequenz.presentation.assistant_afterglow_projection import build_assistant_afterglow_projection  # noqa: E402
from bunkerfrequenz.presentation.event_timeline import build_event_timeline_projection  # noqa: E402
from bunkerfrequenz.presentation.scene_jobs_projection import build_scene_jobs_projection  # noqa: E402

MAX_BODY_BYTES = 64 * 1024
STREET_WORLD_SEED = "bunkerfrequenz-a4-local-street-v1"
DISTRICT_WORLD_SEED = "bunkerfrequenz-a4-local-district-v1"
REQUIRED = (
    "web/a4/index.html",
    "web/a4/styles.css",
    "web/a4/client_resilience.js",
    "web/a4/app.js",
    "web/a4/assistant_jobs_ui.js",
    "web/a4/map_pro.js",
    "web/a4/ui_prefs.js",
    "web/a4/event_timeline.js",
    "web/a4/control_deck_focus.js",
    "web/a4/district_biography.js",
    "web/a4/finance_statement_export.js",
    "web/a4/scene_job_payout_preview.js",
    "web/a4/recovery_actions_ui.js",
    "web/a4/map_usability.js",
    "web/a4/map_usability.css",
    "web/a4/starter.json",
    "manifests/JOURNAL_MANIFEST.json",
    "manifests/INCIDENT_MANIFEST.json",
    "manifests/STREET_ENCOUNTER_MANIFEST.json",
    "manifests/SCENE_JOB_MANIFEST.json",
    "manifests/DISTRICT_STATE_MANIFEST.json",
    "manifests/DISTRICT_EVENT_MANIFEST.json",
    "manifests/CITY_MAP_MANIFEST.json",
    "manifests/PROPERTY_MANIFEST.json",
    "manifests/PROPERTY_UPGRADE_MANIFEST.json",
    "manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json",
    "manifests/HALL_OF_TRIBUTE_MANIFEST.json",
    "manifests/HALL_SEASON_MANIFEST.json",
    "manifests/RANKING_NETWORK_MANIFEST.json",
    "manifests/SYNC_MANIFEST.json",
    "manifests/ZEIT_MANIFEST.json",
    "content/de/ui/street_encounters.json",
    "content/de/ui/district_events.json",
    "content/de/ui/incidents.json",
    "content/de/ui/character_forge.json",
    "content/de/ui/assistant_afterglow.json",
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
        self.street_manifest = _load_json(ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json")
        self.scene_job_manifest = _load_json(ROOT / "manifests" / "SCENE_JOB_MANIFEST.json")
        self.district_manifest = _load_json(ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json")
        self.district_event_manifest = _load_json(ROOT / "manifests" / "DISTRICT_EVENT_MANIFEST.json")
        self.city_map_manifest = _load_json(ROOT / "manifests" / "CITY_MAP_MANIFEST.json")
        self.property_manifest = _load_json(ROOT / "manifests" / "PROPERTY_MANIFEST.json")
        self.property_upgrade_manifest = _load_json(ROOT / "manifests" / "PROPERTY_UPGRADE_MANIFEST.json")
        self.map_pro_manifest = _load_json(ROOT / "manifests" / "BERLIN_OPS_MAP_PRO_MANIFEST.json")
        self.hall_manifest = _load_json(ROOT / "manifests" / "HALL_OF_TRIBUTE_MANIFEST.json")
        self.hall_season_manifest = _load_json(ROOT / "manifests" / "HALL_SEASON_MANIFEST.json")
        self.ranking_manifest = _load_json(ROOT / "manifests" / "RANKING_NETWORK_MANIFEST.json")
        self.sync_manifest = _load_json(ROOT / "manifests" / "SYNC_MANIFEST.json")
        self.zeit_manifest = _load_json(ROOT / "manifests" / "ZEIT_MANIFEST.json")
        self.ranking_text_catalog = _load_json(ROOT / "content" / "de" / "ui" / "character_forge.json")
        self.street_texts = _load_json(ROOT / "content" / "de" / "ui" / "street_encounters.json")
        self.district_event_texts = _load_json(ROOT / "content" / "de" / "ui" / "district_events.json")
        self.incident_texts = _load_json(ROOT / "content" / "de" / "ui" / "incidents.json")
        self.assistant_afterglow_texts = _load_json(ROOT / "content" / "de" / "ui" / "assistant_afterglow.json")
        for encounter in self.street_manifest.get("encounters", ()):
            if not isinstance(encounter, dict):
                raise SystemExit("START FEHLGESCHLAGEN – Street-Katalog ist ungültig")
            for field in ("title_key", "body_key"):
                key = encounter.get(field)
                if not isinstance(key, str) or key not in self.street_texts:
                    raise SystemExit(f"START FEHLGESCHLAGEN – Street-Text fehlt: {key}")
        for approach in self.street_manifest.get("approaches", ()):
            if not isinstance(approach, dict):
                raise SystemExit("START FEHLGESCHLAGEN – Street-Ansatz ist ungültig")
            for field in ("label_key", "description_key"):
                key = approach.get(field)
                if not isinstance(key, str) or key not in self.street_texts:
                    raise SystemExit(f"START FEHLGESCHLAGEN – Street-Ansatztext fehlt: {key}")

        allowed = set(journal_manifest.get("event_types", ()))
        if not allowed:
            raise SystemExit("START FEHLGESCHLAGEN – JOURNAL_MANIFEST besitzt keine Eventtypen")
        self.game_version = str(journal_manifest.get("version", "0.8.6-b1"))
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
        self.session = AssistantGameClientSession(
            self.kernel,
            incident_catalog=self.incident_catalog,
            incident_contract_version=incident_manifest["version"],
            street_manifest=self.street_manifest,
            street_world_seed=STREET_WORLD_SEED,
            scene_job_manifest=self.scene_job_manifest,
            district_manifest=self.district_manifest,
            city_map_manifest=self.city_map_manifest,
            district_event_manifest=self.district_event_manifest,
            district_world_seed=DISTRICT_WORLD_SEED,
            property_manifest=self.property_manifest,
            property_upgrade_manifest=self.property_upgrade_manifest,
        )
        self.starter = _load_json(ROOT / "web" / "a4" / "starter.json")
        self.lock = threading.RLock()

    def projection(self) -> dict:
        with self.lock:
            confirmed_state = self.session.read_state()
            records = self.kernel.read_records()
            projection = build_a4_game_projection(
                confirmed_state,
                incident_catalog=self.incident_catalog,
                district_manifest=self.district_manifest,
                city_map_manifest=self.city_map_manifest,
                property_manifest=self.property_manifest,
                property_upgrade_manifest=self.property_upgrade_manifest,
                map_pro_manifest=self.map_pro_manifest,
                hall_manifest=self.hall_manifest,
                ranking_manifest=self.ranking_manifest,
                sync_manifest=self.sync_manifest,
                ranking_text_catalog=self.ranking_text_catalog,
                hall_season_manifest=self.hall_season_manifest,
                zeit_manifest=self.zeit_manifest,
                street_manifest=self.street_manifest,
                street_text_catalog=self.street_texts,
            )
            projection["scene_jobs"] = build_scene_jobs_projection(
                confirmed_state,
                self.session.scene_jobs.jobs if self.session.scene_jobs is not None else (),
            )
            projection["scene_jobs"]["assistant_afterglow"] = build_assistant_afterglow_projection(
                records,
                self.session.scene_jobs.jobs if self.session.scene_jobs is not None else (),
                self.assistant_afterglow_texts,
            )
            projection["event_timeline"] = build_event_timeline_projection(
                records,
                street_text_catalog=self.street_texts,
                district_event_manifest=self.district_event_manifest,
                district_text_catalog=self.district_event_texts,
                incident_catalog=self.incident_catalog,
                incident_text_catalog=self.incident_texts,
            )
            return projection

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

            if command.get("type") in {"profile.update", "street.walk", "job.run", "assistant.control"}:
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
        if result.metadata:
            payload["metadata"] = deepcopy(result.metadata)
            encounter = payload["metadata"].get("street_encounter")
            if isinstance(encounter, dict):
                title_key = encounter.get("title_key")
                body_key = encounter.get("body_key")
                encounter["title"] = self.street_texts.get(title_key, title_key)
                encounter["body"] = self.street_texts.get(body_key, body_key)
        return payload


class A4RequestHandler(http.server.SimpleHTTPRequestHandler):
    server_version = "BunkerfrequenzA4/0.8.8-b1"

    @property
    def runtime(self) -> A4ClientRuntime:
        return self.server.runtime  # type: ignore[attr-defined]

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def _json(self, status: int, payload: dict) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
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
        launch_url = f"{url}?startup={uuid.uuid4().hex}"
        threading.Timer(0.25, webbrowser.open, args=(launch_url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSTATUS: BEENDET")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
