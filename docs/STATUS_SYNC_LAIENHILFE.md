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

## Praktisches Beispiel nach PR #200

PR #200 hat die bereits echte District-Ursache→Folge-Geschichte erstmals auch **verständlich sichtbar** gemacht. Die vorhandene Timeline projiziert bestätigte `world.district_followup_resolved`-Records und zeigt `Folge von: …` nur, wenn Parent, Bezirk und Journal-Reihenfolge wirklich zusammenpassen.

Fehlt der Parent, gehört er zu einem anderen Bezirk oder liegt die Reihenfolge falsch, wird keine Ursache erfunden. Der Browser schreibt dabei nichts zurück; er erklärt ausschließlich die bestätigte Projection.

Direkt nach diesem fachlichen Safe Merge standen die drei kanonischen Statusdateien noch auf PR #198 und nannten die Read-only-Projection weiterhin als offene Arbeit. Genau diese Abweichung ist Statusdrift.

Die Statuskorrektur übernimmt deshalb PR #200 als gemeinsamen Anker und setzt die nächste aktive Phase desselben `POOL-WORLD-003` auf **`0.8.8-STORY-DISTRICT-MICRO-STORY-002-AUDIT`**.

Dieser Audit baut noch **keine** zweite Story. Er vergleicht zuerst die drei übrigen District-Ereignisse:

- `district.word_of_mouth_wave` – soziale Dynamik und Gerüchte,
- `district.patrol_sweep` – Druck, Erinnerung und kollektive Vorsicht,
- `district.temporary_space_opens` – kurze Gelegenheit, Verlust und möglicher Mythos.

Vorläufig ist `district.temporary_space_opens` dramaturgisch besonders interessant: Die erste Geschichte folgt dem Muster **Störung → Wiederkehr → Erinnerung**. Ein temporärer Raum kann dagegen **Chance → kurze Ekstase → Verlust → Mythos** erzählen. Das erweitert die emotionale Bandbreite, ohne die bestehende Kettenarchitektur zu verändern.

### Merksatz für Laien

**Erst muss das Spiel beweisen, was passiert ist. Dann darf die Oberfläche erklären, wie es zusammenhängt. Und erst danach lohnt sich die nächste Geschichte.**

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
