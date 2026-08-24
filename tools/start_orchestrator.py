#!/usr/bin/env python3
"""Single-path autostart orchestrator for the local BUNKERFREQUENZ client."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import queue
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from typing import Iterable

from start_a4_acceptance import browser_dom, probe_http

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "tools" / "start_a4_game_client.py"
START_SCRIPT = ROOT / "START_BUNKERFREQUENZ.sh"
DESKTOP = ROOT / "BUNKERFREQUENZ.desktop"
DEFAULT_SAVE_DIR = Path.home() / ".local" / "share" / "bunkerfrequenz" / "a4-alpha"
REQUIRED_FILES = (
    SERVER,
    ROOT / "tools" / "start_a4_acceptance.py",
    ROOT / "web" / "a4" / "index.html",
    ROOT / "manifests" / "JOURNAL_MANIFEST.json",
)
GREEN = "🟢"
YELLOW = "🟡"
RED = "🔴"
INFO = "🔵"


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

    def diagnose(self, reason: str, actions: Iterable[str]) -> None:
        lines = [
            "BUNKERFREQUENZ STARTDIAGNOSE",
            f"GRUND: {reason}",
            f"PROJEKTORDNER: {ROOT}",
            f"PYTHON: {sys.version.splitlines()[0]}",
            f"STATUSDATEI: {self.status_path}",
            "",
            "EMPFOHLENE SCHRITTE:",
        ]
        lines.extend(f"- {action}" for action in actions)
        if self.resolutions:
            lines.extend(("", "BEREITS AUTOMATISCH AUFGELÖST:"))
            lines.extend(f"- {item}" for item in self.resolutions)
        self.diagnosis_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"DIAGNOSE: {self.diagnosis_path}", file=sys.stderr, flush=True)

    def _flush(self) -> None:
        lines = ["BUNKERFREQUENZ STARTSTATUS", ""]
        lines.extend(
            f"[{item.progress:>3}%] {item.status} {item.label} – {item.detail}"
            for item in self.results
        )
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
        if self.process.stdout is not None:
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


def _browser_command(address: str) -> tuple[list[str] | None, str]:
    candidates = (
        ("xdg-open", [address]),
        ("firefox", ["--new-tab", address]),
        ("google-chrome", [address]),
        ("google-chrome-stable", [address]),
        ("chromium", [address]),
        ("chromium-browser", [address]),
    )
    for name, args in candidates:
        executable = shutil.which(name)
        if executable:
            return [executable, *args], name
    return None, "kein unterstützter Browserstarter"


def _launch_checked(command: list[str]) -> bool:
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.4)
    if process.poll() is None:
        return True
    return process.returncode == 0


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
    reporter.diagnose(reason, actions)
    return 1


def run(args: argparse.Namespace) -> int:
    reporter = Reporter()
    server: ServerProcess | None = None
    keep_server = False
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
        reporter.step(10, GREEN, "VORPRÜFUNG", "Programmdateien und Python sind verwendbar.")

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

        address = ""
        for attempt in (1, 2):
            server = ServerProcess(save_dir, port)
            reporter.step(40, INFO, "SERVERSTART", f"Lokaler Server startet (Versuch {attempt}/2).")
            server.start()
            try:
                address = server.wait_for_address(args.startup_timeout)
            except (RuntimeError, TimeoutError) as exc:
                server.stop()
                if attempt == 1:
                    reporter.resolution(
                        f"Erster Serverstart scheiterte ({exc}); einmaliger Recovery-Neustart mit freiem Port."
                    )
                    port = 0
                    continue
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
            break
        if not address or server is None:
            return _fail(
                reporter,
                48,
                "SERVERSTART",
                "Serverstart konnte nicht abgeschlossen werden.",
                ("START_DIAGNOSE.txt prüfen.",),
            )
        reporter.step(50, GREEN, "SERVERSTART", f"Lokale Adresse bereit: {address}")

        try:
            probe_http(address)
        except Exception as first_exc:
            reporter.resolution(
                f"API war noch nicht bereit ({first_exc}); automatische Kurz-Nachprüfung."
            )
            time.sleep(0.5)
            try:
                probe_http(address)
            except Exception as exc:
                return _fail(
                    reporter,
                    62,
                    "API-PRÜFUNG",
                    f"/api/health oder /api/state ist nicht sicher erreichbar: {exc}",
                    (
                        "START_DIAGNOSE.txt prüfen.",
                        "Server neu starten; bei Wiederholung das Diagnoseprotokoll melden.",
                    ),
                )
        reporter.step(
            65,
            GREEN,
            "API-PRÜFUNG",
            "/api/health und /api/state sind bestätigt erreichbar.",
        )

        browser_command, browser_name = _browser_command(address)
        ui_verified = False
        try:
            dom = browser_dom(address, require_browser=False, timeout=15.0)
            ui_verified = dom is not None
        except RuntimeError as exc:
            return _fail(
                reporter,
                75,
                "BROWSERPRÜFUNG",
                f"UI-Reaktionsprüfung fehlgeschlagen: {exc}",
                (
                    "Browser-Tab schließen und neu starten.",
                    "Bei Wiederholung START_DIAGNOSE.txt zusammen mit der Fehlermeldung prüfen.",
                ),
            )

        if ui_verified:
            reporter.step(
                78,
                GREEN,
                "BROWSERPRÜFUNG",
                "JavaScript-UI erreicht im automatischen Browsercheck ● BEREIT.",
            )
        elif browser_command is not None:
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

        if args.no_browser:
            reporter.step(84, YELLOW, "BROWSERSTART", f"Automatik deaktiviert. Manuell öffnen: {address}")
        elif browser_command is None:
            reporter.step(
                84,
                YELLOW,
                "BROWSERSTART",
                f"Browser konnte nicht automatisch geöffnet werden. Manuell öffnen: {address}",
            )
        elif _launch_checked(browser_command):
            reporter.step(84, GREEN, "BROWSERSTART", f"{browser_name} wurde für {address} aufgerufen.")
        else:
            reporter.step(
                84,
                YELLOW,
                "BROWSERSTART",
                f"{browser_name} scheiterte; manuell öffnen: {address}",
            )

        if not server.alive():
            return _fail(
                reporter,
                92,
                "NACHVALIDIERUNG",
                "Server wurde nach dem Browserstart unerwartet beendet.",
                ("START_DIAGNOSE.txt prüfen.",),
            )
        try:
            probe_http(address)
        except Exception as exc:
            return _fail(
                reporter,
                92,
                "NACHVALIDIERUNG",
                f"Server lebt, aber API-Nachprüfung scheitert: {exc}",
                ("START_DIAGNOSE.txt prüfen.",),
            )
        reporter.step(
            95,
            GREEN,
            "NACHVALIDIERUNG",
            "Server lebt; Health und bestätigter State sind nach Browserübergabe weiter verfügbar.",
        )

        final_green = ui_verified and (args.no_browser or browser_command is not None)
        final_status = GREEN if final_green else YELLOW
        detail = (
            f"Start vollständig validiert. Adresse: {address}"
            if final_green
            else f"Spielserver ist bereit; mindestens ein optionaler Browserkomfortpunkt bleibt manuell. Adresse: {address}"
        )
        reporter.step(100, final_status, "BEREIT", detail)

        if args.exit_after_ready:
            return 0

        print("STOPP: Strg+C", flush=True)
        keep_server = True
        assert server.process is not None
        try:
            return server.process.wait()
        except KeyboardInterrupt:
            keep_server = False
            server.stop()
            return 0
    finally:
        if server is not None and (args.exit_after_ready or not keep_server):
            server.stop()


def main(argv: list[str] | None = None) -> int:
    return run(parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
