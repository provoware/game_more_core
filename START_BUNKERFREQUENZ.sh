#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON_BIN=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
    PYTHON_BIN="$candidate"
    break
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  printf '%s\n' "[  0%] 🔴 VORPRÜFUNG – Python 3.10 oder neuer wurde nicht gefunden." >&2
  printf '%s\n' "LÖSUNG FÜR UBUNTU/KUBUNTU: sudo apt install python3" >&2
  exit 1
fi

exec "$PYTHON_BIN" tools/start_orchestrator.py "$@"
