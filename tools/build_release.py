#!/usr/bin/env python3
"""Build a deterministic BUNKERFREQUENZ local-alpha ZIP from a Git checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ZIP_TIME = (1980, 1, 1, 0, 0, 0)
ROOT_FILES = {
    "README.md",
    "CHANGELOG.md",
    "TODO.md",
    "VERSION.json",
    "PROJEKTMANIFEST.json",
    "PROJEKTSTATUS.json",
    "START_BUNKERFREQUENZ.sh",
    "BUNKERFREQUENZ.desktop",
}
PREFIXES = ("content/", "docs/", "manifests/", "schemas/", "src/", "web/a4/")
TOOL_FILES = {
    "tools/start_a4_game_client.py",
    "tools/start_a4_acceptance.py",
    "tools/build_release.py",
}


def _run_git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit("RELEASE BUILD FEHLGESCHLAGEN – vollständiger Git-Checkout erforderlich") from exc
    return result.stdout.strip()


def _version() -> str:
    try:
        data = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit("RELEASE BUILD FEHLGESCHLAGEN – VERSION.json ist ungültig") from exc
    version = data.get("version") if isinstance(data, dict) else None
    if not isinstance(version, str) or not version:
        raise SystemExit("RELEASE BUILD FEHLGESCHLAGEN – VERSION.version fehlt")
    return version


def _tracked_modes() -> dict[str, int]:
    raw = subprocess.run(
        ["git", "ls-files", "-s", "-z"], cwd=ROOT, check=True, capture_output=True
    ).stdout.decode("utf-8")
    modes: dict[str, int] = {}
    for record in raw.split("\0"):
        if not record:
            continue
        meta, path = record.split("\t", 1)
        mode = meta.split(" ", 1)[0]
        modes[path] = 0o755 if mode == "100755" else 0o644
    return modes


def _included(path: str) -> bool:
    return path in ROOT_FILES or path in TOOL_FILES or path.startswith(PREFIXES)


def _release_files() -> list[tuple[str, int]]:
    try:
        modes = _tracked_modes()
    except (OSError, subprocess.SubprocessError, UnicodeDecodeError, ValueError) as exc:
        raise SystemExit("RELEASE BUILD FEHLGESCHLAGEN – Git-Dateiliste ist nicht lesbar") from exc
    files: list[tuple[str, int]] = []
    for path in sorted(modes):
        if not _included(path):
            continue
        mode = 0o755 if path == "BUNKERFREQUENZ.desktop" else modes[path]
        files.append((path, mode))
    included = {path for path, _ in files}
    if "START_BUNKERFREQUENZ.sh" not in included:
        raise SystemExit("RELEASE BUILD FEHLGESCHLAGEN – START_BUNKERFREQUENZ.sh fehlt")
    if "BUNKERFREQUENZ.desktop" not in included:
        raise SystemExit("RELEASE BUILD FEHLGESCHLGEN – BUNKERFREQUENZ.desktop fehlt")
    return files


def _write_entry(archive: zipfile.ZipFile, name: str, payload: bytes, mode: int) -> None:
    info = zipfile.ZipInfo(name, ZIP_TIME)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (mode & 0xFFFF) << 16
    archive.writestr(info, payload, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build(output_dir: Path) -> tuple[Path, Path, dict]:
    version = _version()
    source_commit = _run_git("rev-parse", "HEAD")
    source_tree = _run_git("rev-parse", "HEAD^{tree}")
    package_root = f"BUNKERFREQUENZ-{version}"
    files = _release_files()
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"{package_root}.zip"
    sha_path = output_dir / f"{package_root}.zip.sha256"

    release_info = {
        "schema_version": 1,
        "product": "BUNKERFREQUENZ",
        "version": version,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "builder": "tools/build_release.py",
        "file_count": len(files) + 1,
    }
    release_info_bytes = (json.dumps(release_info, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")

    with zipfile.ZipFile(zip_path, "w") as archive:
        for path, mode in files:
            _write_entry(archive, f"{package_root}/{path}", (ROOT / path).read_bytes(), mode)
        _write_entry(archive, f"{package_root}/RELEASE_INFO.json", release_info_bytes, 0o644)

    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    sha_path.write_text(f"{digest}  {zip_path.name}\n", encoding="utf-8")
    summary = {
        **release_info,
        "artifact": zip_path.name,
        "sha256": digest,
        "size_bytes": zip_path.stat().st_size,
    }
    return zip_path, sha_path, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reproduzierbares BUNKERFREQUENZ-Release-ZIP bauen")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args(argv)
    zip_path, sha_path, summary = build(args.output_dir.resolve())
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    print(f"ZIP: {zip_path}")
    print(f"SHA256: {sha_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
