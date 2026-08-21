# Entwicklerhandbuch – BUNKERFREQUENZ

## 1. Einstieg für einen fremden Entwickler

1. `README.md` lesen – Produkt, Baseline und aktive Phase.
2. `PROJEKTSTATUS.json` lesen – tatsächlicher aktueller Entwicklungszustand.
3. `TODO.md` lesen – **nur dort** steht die kanonische nächste Arbeitseinheit.
4. `AGENTS.md` lesen – Arbeits-, PR- und Merge-Regeln.
5. `docs/ARCHITEKTURVERTRAG.md` und den direkten Fachvertrag des Zielbereichs lesen.
6. Betroffene Manifeste/Schemas prüfen.
7. Bestehende Zielstelle ermitteln; keine Parallelimplementierung anlegen.
8. Kleinsten Patch umsetzen und nur die relevanten Gates ausführen.

## 2. Aktueller Projektzustand

- **Runtime-Baseline:** `0.5.2-alpha.1`
- **aktive Entwicklung:** `0.6 – Character Forge Presentation`
- **Runtime:** Python-Standardbibliothek, headless
- **grafisches Framework:** bewusst noch nicht gewählt
- **Sync/Telegram:** noch nicht implementiert

`VERSION.json` bleibt auf der letzten freigegebenen Baseline, bis eine neue Entwicklungsstufe tatsächlich abgenommen wurde. Laufende Arbeit wird in `PROJEKTSTATUS.json` und `TODO.md` geführt.

## 3. Architektur in einem Satz

```text
Domain → Application → Infrastructure
   │           │
   └──────► Presentation → spätere UI

Content/Manifeste/Schemas liefern Regeln und sichtbare Texte.
```

### Grenzen

- Presentation liest/projiziert, schreibt aber nicht direkt in `CharacterState`.
- Schreibaktionen laufen über Application-Services und anschließend Persistence.
- UI-Texte kommen aus `content/`.
- technische IDs bleiben stabil und unsichtbar.
- Journal-Events müssen katalogisiert sein.
- Animationen verändern niemals Game-State.

## 4. Versionierung

Beispiel: `0.5.2-alpha.1`

- `0.x`: aktive Entwicklung vor stabilem 1.0-Release
- Minor-/Patch-Schritt: klar abgegrenzte Entwicklungsstufe oder kompatible Korrektur
- Schemaänderung: eigene `schema_version` plus Migration, wenn bestehende Saves betroffen sind
- Dokument-/Audit-Reparatur ohne neue Produktfunktion erhöht die Produktversion nicht automatisch

## 5. Zielgerichtete Prüfstrategie

Nicht „alles immer testen“, sondern den geänderten Bereich absichern.

### Runtime / Domain / Application / Infrastructure

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
```

Remote-Gate: `.github/workflows/runtime-core.yml`

### Presentation / Character Forge

```bash
PYTHONPATH=src python3 -m compileall -q src/bunkerfrequenz/presentation
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

Remote-Gate: `.github/workflows/presentation-core.yml`

### Action-Vertrag

```bash
python3 tools/validate_action_contract.py
```

### Progressionssimulation

```bash
python3 tools/simulate_characters/progression_simulator.py \
  --runs 1000 --days 720 --seed 90409 \
  --output reports/PROGRESSION_SIMULATION_0.4.1.json
```

## 6. PR-Ablauf

1. Ausgangs-`main` und offene PRs prüfen.
2. Existiert bereits ein PR für dieselbe Zielstelle, wird **kein zweiter konkurrierender PR** eröffnet.
3. Feature-/Fix-Branch anlegen.
4. Nur geplanten Scope ändern.
5. lokale Zielprüfung ausführen.
6. Diff prüfen.
7. PR öffnen.
8. relevante Remote-Gates abwarten.
9. Rot = nicht mergen; Ursache beheben und erneut prüfen.
10. nur den geprüften Head-SHA mergen.
11. überholte Parallel-PRs schließen und erhaltene Ideen in `TODO.md` sichern.

## 7. Definition of Done

Eine Änderung ist abgeschlossen, wenn:

- fachlicher Grund und Abnahme klar sind,
- keine unnötige Nebenänderung enthalten ist,
- direkte Verträge eingehalten werden,
- relevante Tests/CI-Gates grün sind,
- README/TODO/Status/Manifest nur bei echter Zustandsänderung angepasst wurden,
- CHANGELOG die fachliche Änderung nachvollziehbar macht,
- keine konkurrierende Implementierung derselben Zielstelle offen bleibt.

## 8. Fehlerbehandlung

Spieler-/Laienmeldungen bleiben verständlich. Technische Details dürfen separat protokolliert werden, aber nicht als einzige Meldung erscheinen.

Beispiel:

> Der letzte sichere Zustand wurde wiederhergestellt. Die Aktion wurde nicht doppelt übernommen.

statt eines unkommentierten Python-/SQLite-Fehlers.

## 9. Wo nachschlagen?

- Architektur: `docs/ARCHITEKTURVERTRAG.md`
- Datenfluss: `docs/GAME_SCHEMA.md`
- Character/Progression: `docs/CHARACTER_FORGE.md`, `docs/PROGRESSION_CONTRACT.md`
- Actions: `docs/GAMEPLAY_ACTION_CONTRACT.md`
- Persistence/Recovery: `docs/PERSISTENCE_CONTRACT.md`, `docs/RECOVERY_0.5.1.md`
- Presentation: `docs/PRESENTATION_CONTRACT_0.6.md`
- UI/UX: `docs/UI_UX_BLUEPRINT.md`
- Ablage/PR-Regeln: `docs/REPOSITORY_RULES.md`
- Dateisuche: `docs/REPOSITORY_INDEX.md`
