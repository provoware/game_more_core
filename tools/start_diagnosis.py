#!/usr/bin/env python3
"""Pure presentation helpers for BUNKERFREQUENZ startup diagnosis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class FailureClass:
    code: str
    title: str
    explanation: str
    immediate_actions: tuple[str, ...]


_FAILURE_CLASSES = {
    "release_integrity": FailureClass(
        "release_integrity",
        "Release unvollständig oder vermischt",
        "Mindestens eine für den Start notwendige Programmdatei fehlt.",
        (
            "Das vollständige Release-ZIP erneut in einen leeren Ordner entpacken.",
            "Keine Dateien aus unterschiedlichen BUNKERFREQUENZ-Versionen zusammenkopieren.",
        ),
    ),
    "python_runtime": FailureClass(
        "python_runtime",
        "Python-Laufzeit nicht geeignet",
        "Die vorhandene Python-Version erfüllt den Mindestvertrag des Startprogramms nicht.",
        ("Python 3.10 oder neuer bereitstellen und den Start danach erneut ausführen.",),
    ),
    "filesystem_permissions": FailureClass(
        "filesystem_permissions",
        "Spielstandordner oder Dateirechte blockieren",
        "Der lokale Start kann den vorgesehenen Ordner nicht sicher lesen oder beschreiben.",
        (
            "Einen normalen beschreibbaren Benutzerordner als --save-dir verwenden.",
            "Eigentümer und Schreibrechte des Zielordners prüfen; keine pauschalen 777-Rechte setzen.",
        ),
    ),
    "port_configuration": FailureClass(
        "port_configuration",
        "Portkonfiguration ungültig",
        "Die angegebene lokale Portnummer liegt außerhalb des gültigen Bereichs.",
        ("Port 0 für automatische Wahl oder einen Wert zwischen 1 und 65535 verwenden.",),
    ),
    "server_start": FailureClass(
        "server_start",
        "Lokaler Server wird nicht bereit",
        "Der vorhandene A4-Server konnte trotz kontrolliertem Startversuch keine nutzbare Adresse liefern.",
        (
            "Die letzten SERVERSTART-Zeilen in START_STATUS.txt prüfen.",
            "Den Start einmal erneut ausführen; bei Wiederholung START_DIAGNOSE.txt vollständig aufbewahren.",
        ),
    ),
    "api_health": FailureClass(
        "api_health",
        "Lokale API antwortet nicht sicher",
        "Der Serverprozess ist gestartet, aber Health- oder State-Prüfung konnte nicht bestätigt werden.",
        (
            "Andere lokale Programme oder Sicherheitssoftware prüfen, die localhost-Verbindungen blockieren könnten.",
            "Den Start erneut ausführen und bei Wiederholung START_DIAGNOSE.txt mitsenden.",
        ),
    ),
    "browser_validation": FailureClass(
        "browser_validation",
        "Browser-/UI-Prüfung fehlgeschlagen",
        "Die lokale Weboberfläche konnte im automatischen UI-Nachweis nicht den erwarteten Bereitschaftszustand erreichen.",
        (
            "Offene alte BUNKERFREQUENZ-Tabs schließen und den Start erneut ausführen.",
            "Die im Bericht genannte lokale Adresse testweise direkt in Firefox oder Chrome öffnen.",
        ),
    ),
    "post_validation": FailureClass(
        "post_validation",
        "Start verlor nach Übergabe seine Bereitschaft",
        "Der Start war bereits weit fortgeschritten, aber Server oder API waren bei der Nachprüfung nicht mehr stabil erreichbar.",
        (
            "START_STATUS.txt auf die letzte grüne Phase vor NACHVALIDIERUNG prüfen.",
            "Den Start erneut ausführen und bei Wiederholung Diagnose und Statusdatei gemeinsam sichern.",
        ),
    ),
    "unknown_start_failure": FailureClass(
        "unknown_start_failure",
        "Nicht eindeutig klassifizierter Startfehler",
        "Der Start wurde sicher abgebrochen, die Ursache passt aber noch in keine speziellere Fehlerklasse.",
        ("START_STATUS.txt und START_DIAGNOSE.txt gemeinsam prüfen.",),
    ),
}


def classify_failure(label: str, reason: str) -> FailureClass:
    """Map an already detected start failure to a stable presentation class."""
    normalized_label = label.strip().upper()
    normalized_reason = reason.casefold()

    if "pflichtdateien" in normalized_reason or "fehlen" in normalized_reason and normalized_label == "VORPRÜFUNG":
        return _FAILURE_CLASSES["release_integrity"]
    if "python" in normalized_reason and normalized_label == "VORPRÜFUNG":
        return _FAILURE_CLASSES["python_runtime"]
    if "spielstandordner" in normalized_reason or "dateirechte" in normalized_reason:
        return _FAILURE_CLASSES["filesystem_permissions"]
    if "port" in normalized_reason and normalized_label == "ABHÄNGIGKEITEN":
        return _FAILURE_CLASSES["port_configuration"]
    if normalized_label == "SERVERSTART":
        return _FAILURE_CLASSES["server_start"]
    if normalized_label == "API-PRÜFUNG":
        return _FAILURE_CLASSES["api_health"]
    if normalized_label == "BROWSERPRÜFUNG":
        return _FAILURE_CLASSES["browser_validation"]
    if normalized_label == "NACHVALIDIERUNG":
        return _FAILURE_CLASSES["post_validation"]
    return _FAILURE_CLASSES["unknown_start_failure"]


def _deduplicated(items: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        clean = item.strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        result.append(clean)
    return result


def resolution_summary(resolutions: Iterable[str]) -> str:
    items = _deduplicated(resolutions)
    if not items:
        return "0 Bedingungen automatisch gelöst."
    return f"{len(items)} Bedingung(en) automatisch gelöst: " + " | ".join(items)


def render_diagnosis_report(
    *,
    label: str,
    reason: str,
    actions: Iterable[str],
    resolutions: Iterable[str],
    project_root: Path,
    python_version: str,
    status_path: Path,
) -> str:
    """Render a deterministic, beginner-readable diagnosis without changing startup decisions."""
    failure = classify_failure(label, reason)
    resolved = _deduplicated(resolutions)
    immediate = _deduplicated((*failure.immediate_actions, *actions))

    lines = [
        "BUNKERFREQUENZ STARTDIAGNOSE",
        "",
        f"FEHLERKLASSE: {failure.code}",
        f"BEDEUTUNG: {failure.title}",
        f"PHASE: {label}",
        f"GRUND: {reason}",
        f"EINORDNUNG: {failure.explanation}",
        "",
        "JETZT BEHEBEN:",
    ]
    lines.extend(f"{index}. {action}" for index, action in enumerate(immediate, start=1))
    lines.extend(
        (
            "",
            "AUTO-AUFLÖSUNGSBILANZ:",
            resolution_summary(resolved),
        )
    )
    if resolved:
        lines.extend(("", "TRANSPARENTES AUFLÖSUNGSPROTOKOLL:"))
        lines.extend(f"- {item}" for item in resolved)
    lines.extend(
        (
            "",
            "TECHNISCHE ORIENTIERUNG:",
            f"PROJEKTORDNER: {project_root}",
            f"PYTHON: {python_version}",
            f"STATUSDATEI: {status_path}",
            "",
            "SICHERHEIT:",
            "Der Start wurde an dieser Stelle kontrolliert beendet. Der Diagnosehelfer führt selbst keine Reparatur, Installation oder Gameplay-Änderung aus.",
        )
    )
    return "\n".join(lines) + "\n"
