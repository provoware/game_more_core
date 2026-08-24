#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

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

cleanup() {
  local status=$?
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
  fi
  rm -f "$LOG_FILE"
  exit "$status"
}
trap cleanup EXIT INT TERM

python3 tools/start_a4_game_client.py --no-browser "$@" > >(tee "$LOG_FILE") 2>&1 &
SERVER_PID=$!

URL=""
for _ in $(seq 1 120); do
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    wait "$SERVER_PID"
    exit $?
  fi
  URL="$(awk '/^ADRESSE: / {print $2; exit}' "$LOG_FILE" 2>/dev/null || true)"
  if [[ -n "$URL" ]]; then
    break
  fi
  sleep 0.1
done

if [[ -z "$URL" ]]; then
  printf '%s\n' "START FEHLGESCHLAGEN – lokale Spieladresse wurde nicht rechtzeitig bereitgestellt." >&2
  exit 1
fi

printf '%s\n' "SERVER: läuft. Dieses Fenster während des Spielens offen lassen."

launch_checked() {
  "$@" >/dev/null 2>&1 &
  local browser_pid=$!
  sleep 0.6
  if kill -0 "$browser_pid" 2>/dev/null; then
    return 0
  fi
  wait "$browser_pid"
}

open_url() {
  local url="$1"
  if command -v xdg-open >/dev/null 2>&1; then
    if xdg-open "$url" >/dev/null 2>&1; then
      return 0
    fi
  fi
  if command -v firefox >/dev/null 2>&1; then
    if launch_checked firefox --new-tab "$url"; then
      return 0
    fi
  fi
  if command -v google-chrome >/dev/null 2>&1; then
    if launch_checked google-chrome "$url"; then
      return 0
    fi
  fi
  if command -v chromium >/dev/null 2>&1; then
    if launch_checked chromium "$url"; then
      return 0
    fi
  fi
  if command -v chromium-browser >/dev/null 2>&1; then
    if launch_checked chromium-browser "$url"; then
      return 0
    fi
  fi
  return 1
}

if [[ "$AUTO_BROWSER" -eq 1 ]]; then
  if open_url "$URL"; then
    printf '%s\n' "BROWSER: Spieloberfläche wurde geöffnet."
  else
    printf '%s\n' "BROWSER: automatisches Öffnen war nicht möglich."
    printf '%s\n' "BITTE IM BROWSER ÖFFNEN: $URL"
  fi
else
  printf '%s\n' "BROWSER: Automatik deaktiviert. Bitte öffnen: $URL"
fi

printf '%s\n' "STOPP: Strg+C"
wait "$SERVER_PID"
