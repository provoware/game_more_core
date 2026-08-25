# Status-Sync nach Safe Merge – Laienhilfe

## Was wird hier geprüft?

BUNKERFREQUENZ besitzt drei wichtige Projektübersichten: `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json`. Sie sollen denselben zuletzt bestätigten fachlichen `/safe-merge` nennen.

Der Status-Sync-Check liest dafür **nur** die Git-Historie und diese drei vorhandenen Dateien. Er ändert kein Spiel, keinen Spielstand und keine Gameplaywerte.

## Was bedeutet `STATUS SYNC PASS`?

- alle drei Statusdateien nennen denselben Safe-Merge-Anker,
- dieser Anker entspricht dem letzten fachlich relevanten `Safe merge PR #…` in der First-Parent-Historie,
- `PROJEKTSTATUS.json` bestätigt dazu weiterhin `SAFE MERGE PASS` und Main-Provenienz.

## Was bedeutet `STATUS SYNC FAIL`?

Mindestens eine Projektübersicht hängt hinter der bereits gemergten Realität zurück oder widerspricht den anderen beiden Dateien. Der Fehler nennt die betroffene Datei sowie erwartete PR-/Merge-Referenz.

Das ist absichtlich ein **sichtbarer Qualitätsfehler**. Der Check repariert `main` nicht heimlich und führt keinen direkten Bot-Push aus. Die Statuskorrektur bleibt ein normal prüfbarer PR und wird anschließend wieder über `/safe-merge` abgeschlossen.

## Warum erzeugt der Status-Sync-Merge nicht sofort wieder Drift?

Reine Status-Sync-Merges verändern mindestens gemeinsam `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json`. Optional dürfen nur die bereits katalogisierten Status-Sync-Helfer wie Checker, Tests, Workflow, README, Laienhilfe oder passender Changelog-Nachweis dazukommen.

Auch der **kleinste Fall mit ausschließlich den drei kanonischen Statusdateien** wird ausdrücklich als reine Statuskorrektur erkannt. Solche Merges werden bei der Suche nach dem letzten **fachlich relevanten** Safe Merge übersprungen. Dadurch zeigt der Anker weiterhin auf den zuletzt bestätigten Spiel-/QA-/UX-/Story-Slice statt auf seine eigene Dokumentationsreparatur.

Ein beliebiger README-, Test- oder Dokumentations-Merge wird dadurch nicht versteckt: Ohne alle drei kanonischen Statusdateien bleibt er ein normaler relevanter Safe Merge.

## Praktisches Beispiel nach PR #194

PR #194 hat den geplanten District-Ereignisketten-Audit abgeschlossen. Das Ergebnis war absichtlich **kein neuer Gameplay-Code**: Ein bestätigtes `world.district_effect_applied` kann bereits als eindeutige Parent-Evidenz dienen und die District-Quelle ist replaybar. Die Biography bleibt dagegen read-only und darf keine Kette aus Anzeigezustand erzeugen.

Der Audit fand zugleich die harte Grenze: Im Journal existiert noch **kein eigener katalogisierter Child-Eventtyp** für eine District-Folgebegegnung. Deshalb wäre eine Micro-Story an dieser Stelle zu früh und würde den Persistenz-/Replay-Vertrag umgehen.

Direkt nach dem Safe Merge von PR #194 standen die drei kanonischen Statusdateien noch auf PR #192 und führten den bereits erledigten Audit weiterhin als aktive Arbeit. Genau diese Abweichung meldet der Status-Sync als Drift.

Die Statuskorrektur übernimmt deshalb PR #194 als gemeinsamen Anker und setzt die aktive Phase desselben `POOL-WORLD-003` auf **`0.8.8-STORY-DISTRICT-CHAIN-CONTRACT-V1`**. Das ist noch keine Geschichte im Spiel. V1 muss zuerst genau einen Child-Eventtyp, die Parent-Referenz, die District-Bindung und Exactly-once-/Replay-Semantik festlegen.

### Merksatz für Laien

**Erst beweisen, dass A wirklich passiert ist. Dann festlegen, wie B eindeutig auf A zeigt. Erst danach darf B als Geschichte im Spiel passieren.**

So bleibt die Ursache-Wirkungs-Kette verständlich, und ein Retry oder UI-Refresh kann nicht versehentlich eine zweite Storyfolge erzeugen.

## Für Entwickler

Manuelle Prüfung vom Repository-Root:

```bash
python3 tools/status_sync.py check
```

Nur den erkannten Anker anzeigen:

```bash
python3 tools/status_sync.py anchor
```

Die gezielte Regression liegt in `tests/quality/test_status_sync.py`. `tests/runtime/test_feature_status_consistency.py` stellt zusätzlich sicher, dass letzter validierter Feature-Stand, Feature-Pool und nächste aktive Arbeit zusammenpassen.

Der Workflow `.github/workflows/status-sync.yml` führt Regression und Driftprüfung automatisch auf Pull Requests und nach Pushes auf `main` aus.

## Spätere Verbesserungsidee

**STATUS-SYNC-DRIFT-AGE:** Ein späterer rein diagnostischer Slice könnte bei `STATUS SYNC FAIL` zusätzlich ausgeben, wie viele fachlich relevante Safe Merges die Statusquellen hinter dem erkannten Anker liegen. Nutzen: Priorität und Alter einer Drift sind sofort sichtbar, ohne irgendeine Datei automatisch zu schreiben oder den `/safe-merge`-Schutz zu umgehen.
