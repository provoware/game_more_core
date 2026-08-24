#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

DIAG_FILE="$ROOT/START_DIAGNOSE.txt"
rm -f "$DIAG_FILE"

if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' "START FEHLGESCHLAGEN – Python 3 wurde nicht gefunden." >&2
  printf '%s\n' "Ubuntu/Kubuntu: sudo apt install python3" >&2
  exit 1
fi

AUTO_BROWSER=1
for arg in "$@"; do
  if [[ "$arg" == "--no-browser" ]]; then
    AUTO_BROWSER=0
    break
  fi
done

LOG_FILE="$(mktemp -t bunkerfrequenz-start.XXXXXX.log)"
SERVER_PID=""
URL=""

write_diagnosis() {
  local reason="$1"
  {
    printf '%s\n' "BUNKERFREQUENZ STARTDIAGNOSE"
    printf 'GRUND: %s\n' "$reason"
    printf 'PROJEKTORDNER: %s\n' "$ROOT"
    printf 'PYTHON: %s\n' "$(python3 --version 2>&1 || true)"
    printf 'ADRESSE: %s\n' "${URL:-noch nicht verfügbar}"
    printf 'XDG-OPEN: %s\n' "$(command -v xdg-open || echo nicht gefunden)"
    printf 'FIREFOX: %s\n' "$(command -v firefox || echo nicht gefunden)"
    printf 'CHROME: %s\n' "$(command -v google-chrome || command -v google-chrome-stable || echo nicht gefunden)"
    printf 'CHROMIUM: %s\n' "$(command -v chromium || command -v chromium-browser || echo nicht gefunden)"
    printf '%s\n' "--- LETZTE SERVERMELDUNGEN ---"
    tail -n 30 "$LOG_FILE" 2>/dev/null || true
  } > "$DIAG_FILE"
  printf 'DIAGNOSE GESPEICHERT: %s\n' "$DIAG_FILE" >&2
}

cleanup() {
  local status=$?
  trap - EXIT INT TERM
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  rm -f "$LOG_FILE"
  exit "$status"
}
trap cleanup EXIT INT TERM

python3 -u tools/start_a4_game_client.py --no-browser "$@" > >(tee "$LOG_FILE") 2>&1 &
SERVER_PID=$!

for _ in $(seq 1 120); do
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    set +e
    wait "$SERVER_PID"
    SERVER_STATUS=$?
    set -e
    write_diagnosis "Lokaler Spielserver wurde vor der Bereitschaft beendet."
    exit "$SERVER_STATUS"
  fi
  URL="$(awk '/^ADRESSE: / {print $2; exit}' "$LOG_FILE" 2>/dev/null || true)"
  if [[ -n "$URL" ]]; then
    break
  fi
  sleep 0.1
done

if [[ -z "$URL" ]]; then
  write_diagnosis "Lokale Spieladresse wurde nicht rechtzeitig bereitgestellt."
  printf '%s\n' "START FEHLGESCHLAGEN – lokale Spieladresse wurde nicht rechtzeitig bereitgestellt." >&2
  exit 1
fi

if ! python3 tools/start_a4_acceptance.py --address "$URL" --no-browser-check; then
  write_diagnosis "HTTP-Selbsttest für /api/health oder /api/state ist fehlgeschlagen."
  printf '%s\n' "START FEHLGESCHLAGEN – der lokale Server läuft, aber der Spielzustand ist nicht sicher erreichbar." >&2
  exit 1
fi

printf '%s\n' "SERVER: bereit und geprüft. Dieses Fenster während des Spielens offen lassen."
printf 'ADRESSE: %s\n' "$URL"

launch_checked() {
  "$@" >/dev/null 2>&1 &
  local pid=$!
  sleep 0.35
  if kill -0 "$pid" 2>/dev/null; then
    return 0
  fi
  set +e
  wait "$pid"
  local status=$?
  set -e
  [[ "$status" -eq 0 ]]
}

open_url() {
  local url="$1"
  if command -v xdg-open >/dev/null 2>&1 && launch_checked xdg-open "$url"; then
    return 0
  fi
  if command -v firefox >/dev/null 2>&1 && launch_checked firefox --new-tab "$url"; then
    return 0
  fi
  if command -v google-chrome >/dev/null 2>&1 && launch_checked google-chrome "$url"; then
    return 0
  fi
  if command -v google-chrome-stable >/dev/null 2>&1 && launch_checked google-chrome-stable "$url"; then
    return 0
  fi
  if command -v chromium >/dev/null 2>&1 && launch_checked chromium "$url"; then
    return 0
  fi
  if command -v chromium-browser >/dev/null 2>&1 && launch_checked chromium-browser "$url"; then
    return 0
  fi
  return 1
}

if [[ "$AUTO_BROWSER" -eq 1 ]]; then
  if open_url "$URL"; then
    printf '%s\n' "BROWSER: Spieloberfläche wurde geöffnet."
  else
    write_diagnosis "Automatisches Browseröffnen war nicht möglich; der lokale Server ist aber bereit."
    printf '%s\n' "BROWSER: automatisches Öffnen war nicht möglich."
    printf '%s\n' "BITTE IM BROWSER ÖFFNEN: $URL"
  fi
else
  printf '%s\n' "BROWSER: Automatik deaktiviert."
  printf '%s\n' "BITTE IM BROWSER ÖFFNEN: $URL"
fi

printf '%s\n' "STOPP: Strg+C"
wait "$SERVER_PID"
