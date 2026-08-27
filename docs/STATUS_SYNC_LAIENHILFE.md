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

## Praktisches Beispiel nach PR #215

PR #215 hat die zweite Street-Micro-Story **„Der Handschuh wartet noch“** durch den vollständigen Pfad Runtime → Journal/Persistenz → Reload → `/api/state` → echtes Chromium-DOM bewiesen. Gleichzeitig bleibt Story 001 **„Der Tipp macht die Runde“** im selben E2E-Test abgesichert.

Direkt danach standen `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json` noch auf dem alten Anker PR #206. Das Spiel war also weiter als seine drei kanonischen Projektübersichten. Genau diese Abweichung meldet `Status Sync` als Drift.

Die Statuskorrektur übernimmt deshalb PR #215 / `1acceec43514caf7e2e945535896bce9472a19de` als gemeinsamen fachlichen Anker. Der Status-only Safe Merge dieser Korrektur wird anschließend bewusst übersprungen, damit er sich nicht selbst zum neuen Spielstand erklärt.

### Was ist danach der echte nächste Inhaltsschritt?

Nicht sofort Story 003. Zuerst wird mit `0.8.8-STORY-STREET-TONE-DIVERSITY-AUDIT` geprüft, ob die zwei vorhandenen Nachhalle dramaturgisch zu ähnlich sind.

Dabei werden Kandidaten nach vier einfachen Fragen verglichen:

- **sozial:** verändert sich etwas zwischen Menschen oder Gerüchten?
- **räumlich:** erinnert ein Ort sichtbar an eine frühere Begegnung?
- **materiell:** taucht eine Spur oder ein Gegenstand wieder auf, ohne Inventarbonus zu werden?
- **leicht unheimlich:** wirkt die Stadt, als hätte sie sich etwas gemerkt, ohne eine neue Mystery-Engine zu erfinden?

Story 003 darf erst folgen, wenn ein Kandidat deutlich anders wirkt, selten genug ist, eine klare Ursache besitzt, keine Balancewirkung erzeugt und denselben `street.followup_resolved`-Vertrag verwenden kann.

### Merksatz für Laien

**Der Status-Sync sorgt dafür, dass die Projektanzeige nicht hinter dem Spiel herläuft. Er erfindet nichts und repariert nichts heimlich – er zwingt die Dokumentation, die bereits geprüfte Realität korrekt zu nennen.**

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