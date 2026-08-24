#!/usr/bin/env python3
"""Single-path autostart orchestrator for the local BUNKERFREQUENZ client."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import queue
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from typing import Iterable

from start_a4_acceptance import browser_dom, probe_http
from start_diagnosis import render_diagnosis_report, resolution_summary

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "tools" / "start_a4_game_client.py"
START_SCRIPT = ROOT / "START_BUNKERFREQUENZ.sh"
DESKTOP = ROOT / "BUNKERFREQUENZ.desktop"
DEFAULT_SAVE_DIR = Path.home() / ".local" / "share" / "bunkerfrequenz" / "a4-alpha"
REQUIRED_FILES = (
    SERVER,
    ROOT / "tools" / "start_a4_acceptance.py",
    ROOT / "web" / "a4" / "index.html",
    ROOT / "web" / "a4" / "styles.css",
    ROOT / "web" / "a4" / "client_resilience.js",
    ROOT / "web" / "a4" / "map_pro.js",
    ROOT / "web" / "a4" / "ui_prefs.js",
    ROOT / "web" / "a4" / "event_timeline.js",
    ROOT / "web" / "a4" / "app.js",
    ROOT / "web" / "a4" / "assistant_jobs_ui.js",
    ROOT / "web" / "a4" / "control_deck_focus.js",
    ROOT / "web" / "a4" / "district_biography.js",
    ROOT / "web" / "a4" / "finance_statement_export.js",
    ROOT / "web" / "a4" / "scene_job_payout_preview.js",
    ROOT / "web" / "a4" / "recovery_actions_ui.js",
    ROOT / "web" / "a4" / "map_usability.js",
    ROOT / "web" / "a4" / "map_usability.css",
    ROOT / "manifests" / "JOURNAL_MANIFEST.json",
)
GREEN = "🟢"
YELLOW = "🟡"
RED = "🔴"
INFO = "🔵"
RUNTIME_HEALTH_INTERVAL_SECONDS = 10.0
RUNTIME_RECOVERY_WINDOW_SECONDS = 300.0
MAX_RUNTIME_RECOVERIES = 3


@dataclass(frozen=True)
class StepResult:
    progress: int
    status: str
    label: str
    detail: str


class Reporter:
    def __init__(self) -> None:
        requested = os.environ.get("BUNKERFREQUENZ_START_STATE_DIR")
        state_dir = Path(requested).expanduser() if requested else ROOT
        try:
            state_dir.mkdir(parents=True, exist_ok=True)
            probe = state_dir / ".bunkerfrequenz-start-write-probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
        except OSError:
            uid = getattr(os, "getuid", lambda: 0)()
            state_dir = Path(tempfile.gettempdir()) / f"bunkerfrequenz-start-{uid}"
            state_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir = state_dir.resolve()
        self.status_path = self.state_dir / "START_STATUS.txt"
        self.diagnosis_path = self.state_dir / "START_DIAGNOSE.txt"
        self.results: list[StepResult] = []
        self.resolutions: list[str] = []
        self.diagnosis_path.unlink(missing_ok=True)
        self._flush()

    def step(self, progress: int, status: str, label: str, detail: str) -> None:
        result = StepResult(progress, status, label, detail)
        self.results.append(result)
        print(f"[{progress:>3}%] {status} {label} – {detail}", flush=True)
        self._flush()

    def resolution(self, detail: str) -> None:
        self.resolutions.append(detail)
        print(f"      {INFO} AUTO-AUFLÖSUNG – {detail}", flush=True)
        self._flush()

    def diagnose(self, label: str, reason: str, actions: Iterable[str]) -> None:
        report = render_diagnosis_report(
            label=label,
            reason=reason,
            actions=actions,
            resolutions=self.resolutions,
            project_root=ROOT,
            python_version=sys.version.splitlines()[0],
            status_path=self.status_path,
        )
        self.diagnosis_path.write_text(report, encoding="utf-8")
        print(f"DIAGNOSE: {self.diagnosis_path}", file=sys.stderr, flush=True)

    def _flush(self) -> None:
        lines = ["BUNKERFREQUENZ STARTSTATUS", ""]
        lines.extend(
            f"[{item.progress:>3}%] {item.status} {item.label} – {item.detail}"
            for item in self.results
        )
        lines.extend(("", "AUTO-AUFLÖSUNGSBILANZ:", resolution_summary(self.resolutions)))
        if self.resolutions:
            lines.extend(("", "AUTO-AUFLÖSUNGEN:"))
            lines.extend(f"- {item}" for item in self.resolutions)
        try:
            self.status_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except OSError:
            pass


class ServerProcess:
    def __init__(self, save_dir: Path, port: int) -> None:
        self.save_dir = save_dir
        self.port = port
        self.process: subprocess.Popen[str] | None = None
        self.lines: list[str] = []
        self._output: queue.Queue[str | None] = queue.Queue()

    def start(self) -> None:
        command = [
            sys.executable,
            "-u",
            str(SERVER),
            "--port",
            str(self.port),
            "--save-dir",
            str(self.save_dir),
            "--no-browser",
        ]
        self.process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert self.process.stdout is not None

        def read_lines() -> None:
            assert self.process is not None and self.process.stdout is not None
            for line in self.process.stdout:
                clean = line.rstrip()
                self.lines.append(clean)
                self._output.put(line)
                print(clean, flush=True)
            self._output.put(None)

        threading.Thread(target=read_lines, daemon=True).start()

    def wait_for_address(self, timeout: float) -> str:
        if self.process is None:
            raise RuntimeError("Serverprozess wurde nicht gestartet")
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                line = self._output.get(timeout=remaining)
            except queue.Empty:
                break
            if line is None:
                break
            if line.startswith("ADRESSE: "):
                return line.split("ADRESSE: ", 1)[1].strip()
        detail = " | ".join(self.lines[-8:])
        if self.process.poll() is not None:
            raise RuntimeError(f"Server wurde vor Bereitschaft beendet: {detail}")
        raise TimeoutError(f"Server lieferte innerhalb von {timeout:.0f}s keine Adresse: {detail}")

    def alive(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def stop(self) -> None:
        if self.process is None:
            return
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
        if self.process.stdout is not None and not self.process.stdout.closed:
            self.process.stdout.close()


def _port_available(port: int) -> bool:
    if port == 0:
        return True
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def _ensure_save_dir(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=".start-write-probe-", dir=resolved):
        pass
    return resolved


def _ensure_start_permissions(reporter: Reporter) -> None:
    for path in (START_SCRIPT, DESKTOP):
        if not path.exists() or os.access(path, os.X_OK):
            continue
        try:
            path.chmod(path.stat().st_mode | 0o111)
        except OSError as exc:
            reporter.step(
                22,
                YELLOW,
                "STARTRECHTE",
                f"{path.name} konnte nicht automatisch ausführbar gesetzt werden: {exc}",
            )
        else:
            reporter.resolution(f"{path.name} ausführbar gesetzt.")


def _cache_busted_address(address: str, token: str | None = None) -> str:
    launch_token = token or secrets.token_hex(8)
    separator = "&" if "?" in address else "?"
    return f"{address}{separator}startup={launch_token}"


def _browser_candidates(address: str) -> list[tuple[list[str], str]]:
    candidates = (
        ("xdg-open", [address]),
        ("firefox", ["--new-tab", address]),
        ("google-chrome", [address]),
        ("google-chrome-stable", [address]),
        ("chromium", [address]),
        ("chromium-browser", [address]),
    )
    resolved: list[tuple[list[str], str]] = []
    for name, args in candidates:
        executable = shutil.which(name)
        if executable:
            resolved.append(([executable, *args], name))
    return resolved


def _browser_command(address: str) -> tuple[list[str] | None, str]:
    candidates = _browser_candidates(address)
    return candidates[0] if candidates else (None, "kein unterstützter Browserstarter")


def _launch_checked(command: list[str]) -> bool:
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.4)
    if process.poll() is None:
        return True
    return process.returncode == 0


def _launch_browser_with_fallback(
    address: str,
    reporter: Reporter,
    preferred: tuple[list[str] | None, str] | None = None,
) -> tuple[bool, str]:
    candidates = _browser_candidates(address)
    if preferred and preferred[0] is not None:
        preferred_command, preferred_name = preferred
        candidates = [(preferred_command, preferred_name)] + [
            item for item in candidates if item[0][0] != preferred_command[0]
        ]
    if not candidates:
        return False, "kein unterstützter Browserstarter"
    for command, name in candidates:
        try:
            if _launch_checked(command):
                return True, name
        except OSError as exc:
            reporter.resolution(f"Browserstarter {name} war nicht nutzbar ({exc}); nächster vorhandener Starter wird versucht.")
            continue
        reporter.resolution(f"Browserstarter {name} meldete keinen erfolgreichen Start; nächster vorhandener Starter wird versucht.")
    return False, candidates[-1][1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BUNKERFREQUENZ vollautomatisch prüfen und lokal starten"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8044,
        help="Wunschport; bei Belegung wird automatisch ein freier Port gewählt",
    )
    parser.add_argument(
        "--save-dir",
        type=Path,
        default=DEFAULT_SAVE_DIR,
        help="Lokaler Spielstandordner",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Keinen sichtbaren Browser automatisch öffnen",
    )
    parser.add_argument(
        "--exit-after-ready",
        action="store_true",
        help="Nach vollständiger Vor-/Nachvalidierung wieder beenden (CI/Diagnose)",
    )
    parser.add_argument(
        "--startup-timeout",
        type=float,
        default=20.0,
        help="Maximale Wartezeit auf den lokalen Server in Sekunden",
    )
    return parser.parse_args(argv)


def _fail(
    reporter: Reporter,
    progress: int,
    label: str,
    reason: str,
    actions: Iterable[str],
) -> int:
    reporter.step(progress, RED, label, reason)
    reporter.diagnose(label, reason, actions)
    return 1


def _start_server(
    save_dir: Path,
    port: int,
    timeout: float,
    reporter: Reporter,
    *,
    progress: int = 40,
    attempts: int = 2,
) -> tuple[ServerProcess, str]:
    current_port = port
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        server = ServerProcess(save_dir, current_port)
        reporter.step(progress, INFO, "SERVERSTART", f"Lokaler Server startet (Versuch {attempt}/{attempts}).")
        server.start()
        try:
            return server, server.wait_for_address(timeout)
        except (RuntimeError, TimeoutError) as exc:
            last_error = exc
            server.stop()
            if attempt < attempts:
                reporter.resolution(
                    f"Serverstart scheiterte ({exc}); Recovery-Neustart mit automatisch freiem Port."
                )
                current_port = 0
    assert last_error is not None
    raise last_error


def _probe_startup_api(address: str, reporter: Reporter) -> None:
    delays = (0.0, 0.5, 1.0)
    last_error: Exception | None = None
    for attempt, wait_seconds in enumerate(delays, start=1):
        if wait_seconds:
            time.sleep(wait_seconds)
        try:
            probe_http(address)
            return
        except Exception as exc:
            last_error = exc
            if attempt < len(delays):
                reporter.resolution(
                    f"API war noch nicht bereit ({exc}); automatische Nachprüfung {attempt + 1}/{len(delays)}."
                )
    assert last_error is not None
    raise last_error


def _verify_browser_ui(address: str, reporter: Reporter) -> tuple[bool, str]:
    last_error: RuntimeError | None = None
    launch_address = _cache_busted_address(address)
    for attempt in (1, 2):
        try:
            dom = browser_dom(launch_address, require_browser=False, timeout=30.0)
            return dom is not None, launch_address
        except RuntimeError as exc:
            last_error = exc
            if attempt == 1:
                launch_address = _cache_busted_address(address)
                reporter.resolution(
                    f"Erste UI-Reaktionsprüfung scheiterte ({exc}); einmalige Wiederholung mit neuer cache-sicherer Browseradresse."
                )
    assert last_error is not None
    raise last_error


def run(args: argparse.Namespace) -> int:
    reporter = Reporter()
    server: ServerProcess | None = None
    try:
        reporter.step(0, INFO, "START", "Automatische Startprüfung beginnt.")

        missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.is_file()]
        if missing:
            return _fail(
                reporter,
                8,
                "VORPRÜFUNG",
                "Pflichtdateien fehlen: " + ", ".join(missing),
                (
                    "Release-ZIP neu entpacken.",
                    "Keine Einzeldateien aus unterschiedlichen Versionen mischen.",
                ),
            )
        if sys.version_info < (3, 10):
            return _fail(
                reporter,
                8,
                "VORPRÜFUNG",
                f"Python {sys.version_info.major}.{sys.version_info.minor} ist zu alt.",
                ("Python 3.10 oder neuer installieren.",),
            )
        reporter.step(10, GREEN, "VORPRÜFUNG", "Programmdateien, UI-Module und Python sind verwendbar.")

        save_existed = args.save_dir.expanduser().exists()
        try:
            save_dir = _ensure_save_dir(args.save_dir)
        except OSError as exc:
            return _fail(
                reporter,
                20,
                "ABHÄNGIGKEITEN",
                f"Spielstandordner ist nicht beschreibbar: {exc}",
                (
                    "Einen beschreibbaren Ordner mit --save-dir auswählen.",
                    "Dateirechte des Zielordners prüfen.",
                ),
            )
        if not save_existed:
            reporter.resolution(f"Spielstandordner angelegt: {save_dir}")
        _ensure_start_permissions(reporter)

        port = args.port
        if not 0 <= port <= 65535:
            return _fail(
                reporter,
                25,
                "ABHÄNGIGKEITEN",
                f"Ungültiger Port: {port}",
                ("Einen Port zwischen 0 und 65535 verwenden.",),
            )
        if not _port_available(port):
            reporter.resolution(f"Port {port} war belegt; automatischer Wechsel auf freien Port.")
            port = 0
        reporter.step(
            30,
            GREEN,
            "ABHÄNGIGKEITEN",
            f"Spielstandordner bereit; Portstrategie {port}.",
        )

        try:
            server, address = _start_server(save_dir, port, args.startup_timeout, reporter)
        except (RuntimeError, TimeoutError) as exc:
            return _fail(
                reporter,
                48,
                "SERVERSTART",
                str(exc),
                (
                    "START_DIAGNOSE.txt prüfen.",
                    "Spielstandordner und Dateirechte prüfen.",
                ),
            )
        reporter.step(50, GREEN, "SERVERSTART", f"Lokale Adresse bereit: {address}")

        try:
            _probe_startup_api(address, reporter)
        except Exception as exc:
            return _fail(
                reporter,
                62,
                "API-PRÜFUNG",
                f"/api/health oder /api/state ist nach drei begrenzten Prüfungen nicht sicher erreichbar: {exc}",
                (
                    "START_DIAGNOSE.txt prüfen.",
                    "Spielstandordner und Dateirechte prüfen.",
                ),
            )
        reporter.step(
            65,
            GREEN,
            "API-PRÜFUNG",
            "/api/health und /api/state sind bestätigt erreichbar.",
        )

        preferred_browser = _browser_command(_cache_busted_address(address, "candidate"))
        try:
            ui_verified, browser_address = _verify_browser_ui(address, reporter)
        except RuntimeError as exc:
            return _fail(
                reporter,
                75,
                "BROWSERPRÜFUNG",
                f"UI-Reaktionsprüfung blieb auch nach Cache-Recovery fehlerhaft: {exc}",
                (
                    "START_DIAGNOSE.txt prüfen.",
                    "Den alten Browser-Tab schließen; der nächste Start verwendet automatisch neue UI-Asset-Adressen.",
                ),
            )

        if ui_verified:
            reporter.step(
                78,
                GREEN,
                "BROWSERPRÜFUNG",
                "JavaScript-UI erreicht ● BEREIT und die Timeline verlässt ihren Ladezustand.",
            )
        elif preferred_browser[0] is not None:
            reporter.step(
                78,
                YELLOW,
                "BROWSERPRÜFUNG",
                "Kein Chrome/Chromium für DOM-Nachweis; sichtbarer Browserstarter ist vorhanden.",
            )
        else:
            reporter.step(
                78,
                YELLOW,
                "BROWSERPRÜFUNG",
                "Kein unterstützter Browserstarter gefunden; lokale Adresse bleibt manuell nutzbar.",
            )

        browser_started = False
        browser_name = preferred_browser[1]
        if args.no_browser:
            reporter.step(84, YELLOW, "BROWSERSTART", f"Automatik deaktiviert. Manuell öffnen: {browser_address}")
        elif preferred_browser[0] is None:
            reporter.step(
                84,
                YELLOW,
                "BROWSERSTART",
                f"Browser konnte nicht automatisch geöffnet werden. Manuell öffnen: {browser_address}",
            )
        else:
            browser_started, browser_name = _launch_browser_with_fallback(
                browser_address,
                reporter,
                preferred=_browser_command(browser_address),
            )
            if browser_started:
                reporter.step(84, GREEN, "BROWSERSTART", f"{browser_name} wurde mit cache-sicherer Adresse geöffnet.")
            else:
                reporter.step(
                    84,
                    YELLOW,
                    "BROWSERSTART",
                    f"Alle vorhandenen Browserstarter scheiterten; manuell öffnen: {browser_address}",
                )

        post_error: Exception | None = None
        if not server.alive():
            post_error = RuntimeError("Serverprozess wurde nach dem Browserstart beendet")
        else:
            try:
                probe_http(address)
            except Exception as exc:
                post_error = exc

        if post_error is not None:
            reporter.resolution(
                f"Nachvalidierung erkannte einen Server-/API-Ausfall ({post_error}); kontrollierter Recovery-Neustart auf freiem Port."
            )
            server.stop()
            try:
                server, address = _start_server(
                    save_dir,
                    0,
                    args.startup_timeout,
                    reporter,
                    progress=90,
                    attempts=2,
                )
                _probe_startup_api(address, reporter)
            except Exception as exc:
                return _fail(
                    reporter,
                    92,
                    "NACHVALIDIERUNG",
                    f"Automatische Server-Recovery scheiterte: {exc}",
                    ("START_DIAGNOSE.txt prüfen.",),
                )
            browser_address = _cache_busted_address(address)
            if not args.no_browser:
                browser_started, browser_name = _launch_browser_with_fallback(browser_address, reporter)
            reporter.resolution(f"Server-/API-Recovery erfolgreich; neue lokale Adresse: {address}")

        reporter.step(
            95,
            GREEN,
            "NACHVALIDIERUNG",
            "Server lebt; Health und bestätigter State sind nach Browserübergabe weiter verfügbar.",
        )

        final_green = ui_verified and (args.no_browser or browser_started)
        final_status = GREEN if final_green else YELLOW
        detail = (
            f"Start vollständig validiert. Adresse: {browser_address}"
            if final_green
            else f"Spielserver ist bereit; mindestens ein optionaler Browserkomfortpunkt bleibt manuell. Adresse: {browser_address}"
        )
        reporter.step(100, final_status, "BEREIT", detail)

        if args.exit_after_ready:
            return 0

        print("STOPP: Strg+C", flush=True)
        recovery_times: list[float] = []
        consecutive_health_failures = 0
        try:
            while True:
                time.sleep(RUNTIME_HEALTH_INTERVAL_SECONDS)
                runtime_error: Exception | None = None
                if not server.alive():
                    runtime_error = RuntimeError("Serverprozess ist nicht mehr aktiv")
                    consecutive_health_failures = 2
                else:
                    try:
                        probe_http(address)
                        consecutive_health_failures = 0
                        continue
                    except Exception as exc:
                        runtime_error = exc
                        consecutive_health_failures += 1
                        if consecutive_health_failures < 2:
                            reporter.step(
                                97,
                                YELLOW,
                                "LAUFZEIT-WÄCHTER",
                                f"Erste Health-Abweichung erkannt ({exc}); automatische Gegenprüfung folgt.",
                            )
                            continue

                now = time.monotonic()
                recovery_times = [
                    stamp for stamp in recovery_times
                    if now - stamp <= RUNTIME_RECOVERY_WINDOW_SECONDS
                ]
                if len(recovery_times) >= MAX_RUNTIME_RECOVERIES:
                    return _fail(
                        reporter,
                        99,
                        "LAUFZEIT-RECOVERY",
                        f"Recovery-Grenze erreicht: {MAX_RUNTIME_RECOVERIES} Neustarts in {int(RUNTIME_RECOVERY_WINDOW_SECONDS)}s. Letzter Fehler: {runtime_error}",
                        (
                            "START_DIAGNOSE.txt prüfen.",
                            "Wiederkehrende Fehler nicht durch weitere Neustarts verdecken; Ursache anhand des Diagnoseprotokolls beheben.",
                        ),
                    )

                reporter.resolution(
                    f"Laufzeit-Wächter bestätigt Ausfall ({runtime_error}); Server wird kontrolliert neu aufgebaut."
                )
                server.stop()
                try:
                    server, address = _start_server(
                        save_dir,
                        0,
                        args.startup_timeout,
                        reporter,
                        progress=97,
                        attempts=2,
                    )
                    _probe_startup_api(address, reporter)
                except Exception as exc:
                    return _fail(
                        reporter,
                        99,
                        "LAUFZEIT-RECOVERY",
                        f"Server konnte nicht automatisch wiederhergestellt werden: {exc}",
                        ("START_DIAGNOSE.txt prüfen.",),
                    )
                recovery_times.append(time.monotonic())
                consecutive_health_failures = 0
                browser_address = _cache_busted_address(address)
                if not args.no_browser:
                    launched, launched_name = _launch_browser_with_fallback(browser_address, reporter)
                    if launched:
                        reporter.resolution(f"Browser nach Server-Recovery über {launched_name} auf neue Adresse umgeschaltet.")
                    else:
                        reporter.step(
                            98,
                            YELLOW,
                            "LAUFZEIT-RECOVERY",
                            f"Server repariert; Browser bitte manuell öffnen: {browser_address}",
                        )
                reporter.step(
                    98,
                    GREEN,
                    "LAUFZEIT-RECOVERY",
                    f"Server und API wiederhergestellt. Adresse: {address}",
                )
        except KeyboardInterrupt:
            return 0
    finally:
        if server is not None:
            server.stop()


def main(argv: list[str] | None = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())