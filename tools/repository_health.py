#!/usr/bin/env python3
"""Compact repository consistency guard for BUNKERFREQUENZ.

Uses only the Python standard library. It validates repository structure and
information contracts; gameplay rules remain owned by their existing tests.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
GUARD_MANIFEST = ROOT / "manifests" / "REPOSITORY_GUARD_MANIFEST.json"
TEXT_SUFFIXES = {".json", ".md", ".py", ".sh", ".toml", ".txt", ".yaml", ".yml"}
VERSION_RE = re.compile(r"(?<!\d)(\d+)\.(\d+)(?:\.(\d+))?(?!\d)")


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} muss ein JSON-Objekt sein")
    return value


def _tracked_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        items = [item for item in result.stdout.decode("utf-8").split("\0") if item]
        return [ROOT / item for item in items]
    except (OSError, subprocess.SubprocessError, UnicodeDecodeError):
        return [
            path
            for path in ROOT.rglob("*")
            if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts
        ]


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _parse_version(value: object) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    match = VERSION_RE.search(value)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3) or 0)


def _check_json(files: Iterable[Path], errors: list[str]) -> int:
    count = 0
    for path in files:
        if path.suffix.lower() != ".json":
            continue
        count += 1
        try:
            with path.open(encoding="utf-8") as handle:
                json.load(handle)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"JSON ungültig: {_rel(path)}: {exc}")
    return count


def _check_conflict_markers(files: Iterable[Path], errors: list[str]) -> int:
    count = 0
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        count += 1
        left = any(line.startswith("<<<<<<< ") for line in text.splitlines())
        middle = any(line.strip() == "=======" for line in text.splitlines())
        right = any(line.startswith(">>>>>>> ") for line in text.splitlines())
        if left and middle and right:
            errors.append(f"Merge-Konfliktmarker gefunden: {_rel(path)}")
    return count


def _check_python_structure(
    files: Iterable[Path],
    guard: Mapping[str, object],
    errors: list[str],
) -> int:
    definitions: dict[str, list[str]] = defaultdict(list)
    count = 0
    for path in files:
        if path.suffix.lower() != ".py":
            continue
        count += 1
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=_rel(path))
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            errors.append(f"Python-Struktur ungültig: {_rel(path)}: {exc}")
            continue

        names = [
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        ]
        for name, occurrences in Counter(names).items():
            if occurrences > 1:
                errors.append(f"Doppelte Top-Level-Definition {name!r} in {_rel(path)}")
        for name in names:
            definitions[name].append(_rel(path))

        if path.name == "__init__.py":
            all_assignments = 0
            for node in tree.body:
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    if any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets):
                        all_assignments += 1
            if all_assignments > 1:
                errors.append(f"Mehrere __all__-Definitionen in {_rel(path)}")

    canonical = guard.get("canonical_symbols", {})
    if not isinstance(canonical, Mapping):
        errors.append("Guard-Manifest: canonical_symbols muss ein Mapping sein")
        return count
    for symbol, expected_path in canonical.items():
        if not isinstance(symbol, str) or not isinstance(expected_path, str):
            errors.append("Guard-Manifest: canonical_symbols enthält ungültige Einträge")
            continue
        actual = definitions.get(symbol, [])
        if actual != [expected_path]:
            errors.append(
                f"Kanonisches Symbol {symbol!r}: erwartet [{expected_path}], gefunden {actual or 'nichts'}"
            )
    return count


def _check_public_exports(guard: Mapping[str, object], errors: list[str]) -> int:
    packages = guard.get("public_packages", [])
    if not isinstance(packages, list):
        errors.append("Guard-Manifest: public_packages muss eine Liste sein")
        return 0

    sys.path.insert(0, str(ROOT / "src"))
    checked = 0
    try:
        for package_name in packages:
            if not isinstance(package_name, str) or not package_name:
                errors.append("Guard-Manifest: ungültiger Package-Name")
                continue
            checked += 1
            try:
                module = importlib.import_module(package_name)
            except Exception as exc:  # Importfehler müssen als Guard-Fehler sichtbar werden.
                errors.append(f"Öffentliches Package nicht importierbar: {package_name}: {exc}")
                continue
            exports = getattr(module, "__all__", None)
            if not isinstance(exports, (list, tuple)):
                errors.append(f"{package_name} benötigt eine eindeutige __all__-Liste")
                continue
            duplicate_exports = sorted(name for name, amount in Counter(exports).items() if amount > 1)
            if duplicate_exports:
                errors.append(f"Doppelte öffentliche Exporte in {package_name}: {duplicate_exports}")
            missing = sorted(name for name in exports if not isinstance(name, str) or not hasattr(module, name))
            if missing:
                errors.append(f"Nicht auflösbare öffentliche Exporte in {package_name}: {missing}")
    finally:
        try:
            sys.path.remove(str(ROOT / "src"))
        except ValueError:
            pass
    return checked


def _pull_request_has_path_filter(workflow_text: str) -> bool:
    lines = workflow_text.splitlines()
    for index, line in enumerate(lines):
        if line == "  pull_request:":
            for child in lines[index + 1 :]:
                if child.strip() and len(child) - len(child.lstrip()) <= 2:
                    break
                stripped = child.strip()
                if stripped.startswith("paths:") or stripped.startswith("paths-ignore:"):
                    return True
            return False
    return False


def _check_workflows(guard: Mapping[str, object], errors: list[str]) -> int:
    workflows = guard.get("required_workflows", {})
    if not isinstance(workflows, Mapping):
        errors.append("Guard-Manifest: required_workflows muss ein Mapping sein")
        return 0
    checked = 0
    for job_id, relative_path in workflows.items():
        if not isinstance(job_id, str) or not isinstance(relative_path, str):
            errors.append("Guard-Manifest: ungültiger Workflow-Eintrag")
            continue
        checked += 1
        path = ROOT / relative_path
        if not path.is_file():
            errors.append(f"Pflichtworkflow fehlt: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        if "  pull_request:" not in text:
            errors.append(f"Pflichtworkflow läuft nicht auf jedem PR: {relative_path}")
        if _pull_request_has_path_filter(text):
            errors.append(f"Pflichtworkflow besitzt PR-Pfadfilter und kann als Required Check fehlen: {relative_path}")
        if not re.search(rf"^  {re.escape(job_id)}:\s*$", text, re.MULTILINE):
            errors.append(f"Pflicht-Check-ID {job_id!r} fehlt in {relative_path}")
    return checked


def _check_information_contract(guard: Mapping[str, object], errors: list[str]) -> dict[str, str]:
    info = guard.get("canonical_information", {})
    if not isinstance(info, Mapping):
        errors.append("Guard-Manifest: canonical_information muss ein Mapping sein")
        return {}

    required_keys = {"version", "project_manifest", "project_status", "todo", "readme"}
    if set(info) != required_keys:
        errors.append(f"Guard-Manifest: canonical_information benötigt exakt {sorted(required_keys)}")
        return {}

    try:
        version = _load_json(ROOT / str(info["version"]))
        project_manifest = _load_json(ROOT / str(info["project_manifest"]))
        project_status = _load_json(ROOT / str(info["project_status"]))
        todo = (ROOT / str(info["todo"])).read_text(encoding="utf-8")
        readme = (ROOT / str(info["readme"])).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"Informationsvertrag nicht lesbar: {exc}")
        return {}

    baseline = version.get("version")
    active = project_status.get("active_iteration")
    phase = project_manifest.get("active_development_phase")
    project_names = {
        version.get("product"),
        project_manifest.get("canonical_name"),
        project_status.get("project"),
    }
    if len(project_names) != 1 or None in project_names:
        errors.append(f"Projektname widersprüchlich: {sorted(str(name) for name in project_names)}")

    for source, value in (
        ("PROJEKTSTATUS.release_baseline", project_status.get("release_baseline")),
        ("PROJEKTSTATUS.version", project_status.get("version")),
        ("PROJEKTSTATUS.last_validated_release", project_status.get("last_validated_release")),
        ("PROJEKTMANIFEST.release_baseline", project_manifest.get("release_baseline")),
        ("PROJEKTMANIFEST.version", project_manifest.get("version")),
    ):
        if value != baseline:
            errors.append(f"Versionswiderspruch: {source}={value!r}, VERSION.version={baseline!r}")

    if not isinstance(active, str) or _parse_version(active) is None:
        errors.append(f"PROJEKTSTATUS.active_iteration ungültig: {active!r}")
    if not isinstance(phase, str) or _parse_version(phase) is None:
        errors.append(f"PROJEKTMANIFEST.active_development_phase ungültig: {phase!r}")
    if isinstance(active, str) and isinstance(phase, str):
        if not (active == phase or active.startswith(f"{phase}.")):
            errors.append(f"Projektphase widersprüchlich: active_iteration={active}, phase={phase}")

    for document_name, text in (("README.md", readme), ("TODO.md", todo)):
        if isinstance(baseline, str) and baseline not in text:
            errors.append(f"{document_name} nennt Runtime-Baseline {baseline} nicht")
        if isinstance(active, str) and active not in text:
            errors.append(f"{document_name} nennt aktive/nächste Iteration {active} nicht")

    if project_status.get("repository_policy") != "one_active_implementation_pr_per_canonical_target":
        errors.append("PROJEKTSTATUS.repository_policy fehlt oder ist nicht kanonisch")

    return {
        "baseline": str(baseline or ""),
        "active_iteration": str(active or ""),
        "phase": str(phase or ""),
    }


def _check_stale_branch(
    guard: Mapping[str, object],
    info: Mapping[str, str],
    *,
    head_ref: str,
    base_ref: str,
    errors: list[str],
) -> None:
    settings = guard.get("stale_branch_guard", {})
    if not isinstance(settings, Mapping) or settings.get("enabled") is not True:
        return
    protected_branch = guard.get("protected_branch")
    if not head_ref or base_ref != protected_branch:
        return
    exempt_prefixes = settings.get("exempt_prefixes", [])
    if isinstance(exempt_prefixes, list) and any(
        isinstance(prefix, str) and head_ref.startswith(prefix) for prefix in exempt_prefixes
    ):
        return
    head_version = _parse_version(head_ref)
    active_version = _parse_version(info.get("active_iteration"))
    if head_version is not None and active_version is not None and head_version < active_version:
        errors.append(
            f"Überholter Entwicklungsbranch {head_ref!r}: Branch-Version {head_version} < aktive Iteration {active_version}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ Repository Health Guard")
    parser.add_argument("--head-ref", default="", help="PR-Head-Branch für Stale-Branch-Prüfung")
    parser.add_argument("--base-ref", default="", help="PR-Base-Branch für Stale-Branch-Prüfung")
    args = parser.parse_args()

    errors: list[str] = []
    try:
        guard = _load_json(GUARD_MANIFEST)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"REPOSITORY HEALTH FAIL: Guard-Manifest nicht lesbar: {exc}", file=sys.stderr)
        return 2

    files = _tracked_files()
    json_count = _check_json(files, errors)
    text_count = _check_conflict_markers(files, errors)
    py_count = _check_python_structure(files, guard, errors)
    package_count = _check_public_exports(guard, errors)
    workflow_count = _check_workflows(guard, errors)
    info = _check_information_contract(guard, errors)
    _check_stale_branch(
        guard,
        info,
        head_ref=args.head_ref,
        base_ref=args.base_ref,
        errors=errors,
    )

    if errors:
        print("REPOSITORY HEALTH FAIL", file=sys.stderr)
        for error in errors:
            print(f"::error::{error}", file=sys.stderr)
        return 1

    print("REPOSITORY HEALTH PASS")
    print(f"JSON geprüft: {json_count}")
    print(f"Textdateien auf Konfliktmarker geprüft: {text_count}")
    print(f"Python-Dateien strukturell geprüft: {py_count}")
    print(f"Öffentliche Packages geprüft: {package_count}")
    print(f"Pflichtworkflows geprüft: {workflow_count}")
    print(
        "Informationsvertrag: "
        f"Baseline {info.get('baseline')} | Phase {info.get('phase')} | Iteration {info.get('active_iteration')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
