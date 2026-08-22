#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' "START FEHLGESCHLAGEN – Python 3 wurde nicht gefunden." >&2
  printf '%s\n' "Ubuntu/Kubuntu: sudo apt install python3" >&2
  exit 1
fi

exec python3 tools/start_a4_game_client.py "$@"
