# Status-Sync nach PR #261 – Laienhilfe

## Was wurde repariert?

Die Spielmechanik wurde nicht verändert. Nur die drei Projektübersichten `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json` zeigen wieder auf denselben bereits sicher gemergten Stand: PR #261 / `9bf156dbab23cd525587824ddaf361cb27be7019`.

## Woran erkenne ich den sauberen Zustand?

Alle drei kanonischen Dateien nennen denselben Status-Sync-Anker. `python3 tools/status_sync.py check` muss danach `STATUS SYNC PASS` melden. Die Reparaturwerte stammen aus dem bereits vorhandenen read-only Befehl `python3 tools/status_sync.py suggest`; der Befehl selbst schreibt weiterhin nichts.

## Was bedeutet das für das Spiel?

Es gibt dadurch keinen neuen Bonus und keine neue Venue-Mechanik. Die fünf sichtbaren Ortswerte bleiben reine bestätigte Anzeige. Der nächste fachliche Schritt bleibt die getrennte Prüfung, ob genau ein vorhandener Venue-Wert überhaupt eine saubere Settlement-Autorität erhalten darf.

## Spätere Verbesserungsidee

**STATUS-SYNC-SUMMARY:** `suggest` könnte später optional eine kurze Einzeilen-Zusammenfassung wie `3/3 kanonische Dateien zu aktualisieren` beziehungsweise `3/3 synchron` ausgeben. Nutzen: Der Driftzustand wäre für Laien sofort erfassbar, ohne Schreibrechte oder eine zweite Statusquelle einzuführen.
