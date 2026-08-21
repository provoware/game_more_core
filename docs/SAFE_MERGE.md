# Safe Merge – sicherer Mergeweg nach `main`

## Zweck

Solange GitHubs native Branch Protection für `main` nicht technisch erzwungen werden kann, ist `/safe-merge` der verbindliche normale Mergeweg dieses Repositorys.

Der Mechanismus ergänzt die drei bestehenden Gates:

1. `Runtime Core`
2. `Presentation Core`
3. `Repository Health`

Er ersetzt keinen dieser Checks.

## Normaler Ablauf

1. PR gegen `main` öffnen.
2. Warten, bis alle drei Gates grün sind.
3. Sicherstellen, dass der PR den aktuellen `main` enthält.
4. Offene Review-Threads vollständig klären.
5. Als eigenen PR-Kommentar exakt schreiben:

```text
/safe-merge
```

6. Den Bot-Rückkanal im PR prüfen.

## Was `/safe-merge` prüft

Vor dem Merge wird fail-closed geprüft:

- der auslösende Benutzer besitzt `write`, `maintain` oder `admin`,
- der PR ist offen,
- der PR ist kein Draft,
- Zielbranch ist exakt `main`,
- der PR ist mergefähig,
- der PR-Head enthält den aktuellen `main`,
- `Runtime Core`, `Presentation Core` und `Repository Health` sind auf exakt diesem Head erfolgreich,
- es existieren keine ungelösten Review-Threads,
- der PR verändert keine geschützte Guard-/CI-Sicherheitsdatei.

Erst danach wird GitHubs Merge-API mit dem erwarteten PR-Head-SHA aufgerufen.

## Genau-einmal-Merge

Der Merge-API-Aufruf wird genau einmal ausgeführt.

GitHubs API kann unmittelbar nach einem erfolgreichen Merge kurzzeitig noch keine Commit→PR-Assoziation liefern. Deshalb wird **nur die nachgelagerte Provenienz-Leseprüfung** mit begrenzten Wartezeiten wiederholt:

```text
0 s → 1 s → 2 s → 4 s → 8 s
```

Der Merge selbst wird dabei niemals erneut ausgelöst.

## Rückmeldungen

### `SAFE MERGE PASS`

Der exakte geprüfte Head wurde gemergt und die Main-Provenienz anschließend bestätigt.

### `SAFE MERGE BLOCKED`

Der Merge wurde **nicht** ausgeführt. Mindestens eine Vorbedingung ist nicht erfüllt, zum Beispiel:

- roter oder fehlender Gate,
- veralteter Branch,
- Draft,
- ungelöster Review-Thread,
- fehlende Berechtigung,
- Mergekonflikt.

Zuerst den genannten Fehler beheben, dann die Gates erneut prüfen.

### `SAFE MERGE COMMITTED – POST-VERIFY NICHT BESTÄTIGT`

Der Merge wurde bereits geschrieben, aber GitHubs nachgelagerte Provenienzabfrage konnte auch nach den begrenzten Retries noch nicht bestätigt werden.

**Wichtig:** In diesem Zustand `/safe-merge` nicht einfach erneut auslösen. Zuerst prüfen:

- ist der PR bereits als `merged` markiert,
- welcher Merge-Commit wurde erzeugt,
- ob `Main Integrity` einen Incident meldet.

## Main Integrity

`.github/workflows/main-integrity.yml` prüft normale Updates von `main` zusätzlich auf Provenienz:

- normaler Zwei-Eltern-PR-Merge,
- genau ein zugehöriger gemergter PR nach `main`,
- ursprünglicher PR-Head mit allen drei grünen Pflichtworkflows,
- keine ungelösten Review-Threads.

Kann diese Provenienz nach begrenztem Retry nicht bestätigt werden, wird ein `[MAIN-INTEGRITY]`-Incident angelegt.

## Geschützte Guard-Dateien

Normale `/safe-merge`-PRs dürfen die Sicherheitsgrenze nicht selbst verändern. Dazu gehören insbesondere:

- die drei Kern-Gate-Workflows,
- `safe-merge.yml`,
- `main-integrity.yml`,
- Repository-Health- und Merge-Guard-Tools,
- Guard-Manifest,
- Guard-Tests.

Änderungen daran benötigen einen ausdrücklich auditierten Security-Bootstrap-PR mit allen drei grünen Gates.

## Native Branch Protection

Native GitHub Branch Protection bleibt der bevorzugte langfristige zusätzliche Schutz. Solange sie nicht aktiviert ist, ist `/safe-merge` plus `Main Integrity` der operative Schutzpfad für normale PRs.

Native Zielpolicy für `main`:

- Pull Request erforderlich,
- Branch vor Merge aktuell,
- Required Checks: `runtime-core`, `presentation-core`, `repository-health`,
- Conversation Resolution erforderlich,
- keine Force Pushes,
- kein Branch-Löschen.
