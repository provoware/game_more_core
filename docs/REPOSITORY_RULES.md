# Repository-Regeln: Ablage, Wahrheit und PR-Lebenszyklus

## Zweck

Diese Regeln halten das Repository klein, eindeutig und übernehmbar. Jede Information besitzt genau einen zuständigen Ort; Kopien, konkurrierende Implementierungen und widersprüchliche Statusangaben werden vermieden.

## Einordnung

| Art | Ort | Enthält | Enthält nicht |
|---|---|---|---|
| Runtime-Code | `src/` | ausführbare Spiellogik und technische Adapter | Entwickler-Skripte, sichtbare Texte |
| Basistool | `tools/` | kleines direkt ausführbares Hilfsprogramm | Fachvertrag, Runtime-Code, lange Anleitung |
| Dokumentation | `docs/` | Erklärung, Architekturentscheidung, Anleitung | doppelte Zahlenregeln |
| Manifest | `manifests/` | kanonische maschinenlesbare Fachregeln/Kataloge | Erläuterung als zweite Wahrheit |
| Schema | `schemas/` | Struktur- und Typverträge | Laufzeitdaten |
| Inhalt | `content/` | lokalisierte sichtbare Texte und Figureninhalte | technische Regeln |
| Test | `tests/` | prüfbare Erwartungen an direkte Verträge | Produktionslogik |
| Bericht | `reports/` | reproduzierbarer Prüfnachweis | volatile Laufdaten ohne Freigabegrund |

## Informationshierarchie

- `VERSION.json` = letzte versionierte Produkt-/Runtime-Baseline.
- `PROJEKTSTATUS.json` = tatsächlich aktive Entwicklungsiteration und nächstes Ziel.
- `TODO.md` = kanonische offene Arbeit in Ausführungsreihenfolge.
- `CHANGELOG.md` = historische Änderungsspur; keine Aufgabenliste.
- `README.md` = Einstieg und Navigation; keine zweite Spezifikation.
- Fachverträge/Manifeste/Schemas = verbindliche technische Wahrheit für ihren Bereich.

Eine laufende spätere Entwicklungsiteration darf bei einer älteren freigegebenen `VERSION.json`-Baseline stehen, solange die neue Stufe noch keine eigene freigegebene Produktbaseline ist.

## Was als Basistool gilt

Ein Basistool unter `tools/` muss:

1. genau eine Entwicklungsaufgabe lösen,
2. direkt über die Kommandozeile startbar sein,
3. keine Spiel-UI importieren,
4. kanonische Regeln aus Manifesten/Schemas lesen statt kopieren,
5. möglichst nur die Standardbibliothek verwenden,
6. bei Zufall einen expliziten Seed besitzen,
7. bei erzeugten Dateien Quelle, Parameter und Ziel dokumentieren.

Unterverzeichnisse sind nur nötig, wenn ein Tool mehrere eng zusammengehörige Dateien besitzt.

## PR-Regel

### Eine kanonische Zielstelle – ein aktiver Implementierungs-PR

Mehrere parallele PRs dürfen nicht gleichzeitig unterschiedliche Varianten derselben Datei oder desselben Moduls anbieten. Das erzeugt Konflikte, doppelte Tests und unklare Wahrheit.

Bei konkurrierenden Ansätzen:

1. Nutzen und Unterschiede kurz prüfen.
2. Erhaltenswerte Punkte in `TODO.md` konsolidieren.
3. Einen kanonischen nächsten Implementierungsweg bestimmen.
4. Überholte PRs mit Begründung schließen.
5. Den verbleibenden Weg auf aktuellem `main` neu bzw. sauber weiterführen.

### Merge-Gate

Für Pull Requests nach `main` sind drei stabile Check-IDs vorgesehen:

- `runtime-core`
- `presentation-core`
- `repository-health`

Alle drei müssen vorhanden und grün sein. Ein fehlender Check wird nicht als neutral behandelt. Lokale Tests dürfen einen roten oder fehlenden Remote-Gate nicht überstimmen. Der geprüfte Head-SHA muss zur Merge-Entscheidung passen.

Der PR-Head muss außerdem den aktuellen `main` enthalten. Ein veralteter Branch wird vor dem Merge aktualisiert oder rebased. Alte versionsgebundene Feature-Branches unterhalb der aktiven Entwicklungsiteration sind keine gültige Merge-Quelle.

Die maschinenlesbare Zielpolicy steht in `manifests/REPOSITORY_GUARD_MANIFEST.json`; technische Hintergründe und GitHub-Aktivierung stehen in `docs/REPOSITORY_GUARD.md`.

## CI-Zuständigkeit

- `.github/workflows/runtime-core.yml` schützt Runtime-/Domain-/Application-/Infrastructure-Verhalten.
- `.github/workflows/presentation-core.yml` schützt die Character-Forge-Presentation, ihre Tests und UI-Textkataloge.
- `.github/workflows/repository-health.yml` schützt Repository-Struktur, Informationskonsistenz, Branch-Aktualität, kanonische Symbole und öffentliche Exporte.

Alle drei Workflows laufen auf jedem Pull Request, damit ihre Check-IDs zuverlässig als Required Checks verwendet werden können. Der Repository-Health-Check ersetzt keine Fachtests.

## Repository Health

`tools/repository_health.py` nutzt nur die Python-Standardbibliothek und prüft unter anderem:

- JSON-Syntax aller getrackten JSON-Dateien,
- echte Git-Konfliktmarker,
- Python-Struktur und öffentliche Exporte,
- eindeutige kanonische Presentation-Symbole,
- Versions-/Status-/Phasen-Konsistenz,
- Pflichtworkflows ohne PR-Pfadfilter,
- alte versionsgebundene Feature-Branches gegen die aktive Iteration.

Der GitHub-Workflow prüft zusätzlich, dass der PR-Head den aktuellen Base-Branch enthält.

## Branch Protection

Zielzustand für `main`:

- Pull Request erforderlich,
- Branch vor Merge aktuell,
- offene Review-Konversationen aufgelöst,
- `runtime-core`, `presentation-core`, `repository-health` als Required Checks,
- Force Pushes aus,
- Branch-Löschen aus.

Die Repository-Regel darf nur als aktiv dokumentiert werden, wenn GitHub sie tatsächlich aktiviert hat. Die aktuell verbundene GitHub-Schnittstelle besitzt keine sichere Schreibaktion für Branch-Protection/Rulesets; deshalb bleibt die Aktivierung ein explizit dokumentierter externer GitHub-Schritt.

## Was Dokumentation leisten muss

- Markdown erklärt **warum** und **wie**.
- Zahlen, IDs und Eventtypen werden nicht als zweite Wahrheit gepflegt, wenn ein Manifest zuständig ist.
- Bilder liegen unter `docs/assets/`.
- Ein Statusdokument nennt klar, ob eine Prüfung lokal, remote oder noch offen ist.
- Historische Berichte werden nicht rückwirkend als Eingabe der Runtime verwendet.

## Entscheidungsweg für neue Dateien

```text
Muss die Datei im Spiel ausgeführt werden?           → src/
Ist sie ein kleines Entwicklerwerkzeug?              → tools/
Definiert sie maschinenlesbare Fachregeln?           → manifests/
Definiert sie eine Datenstruktur?                    → schemas/
Ist sie sichtbarer/lokalisierter Inhalt?             → content/
Prüft sie einen Vertrag?                             → tests/
Belegt sie einen reproduzierbaren Prüflauf?          → reports/
Erklärt sie einen Zusammenhang?                      → docs/
```

Im Zweifel wird zuerst die bestehende zuständige Stelle gesucht.

## Bestehende Basiswerkzeuge

| Tool | Aufgabe | Kanonische Eingaben |
|---|---|---|
| `tools/validate_action_contract.py` | Action-Gewichte und Referenzen prüfen | Action-, Skill-, Trait- und Journal-Manifeste |
| `tools/simulate_characters/progression_simulator.py` | Progression deterministisch simulieren | Progression- und Trait-Engine-Manifeste |
| `tools/repository_health.py` | Merge-/Repository-Konsistenz fail-closed prüfen | `REPOSITORY_GUARD_MANIFEST.json` + kanonische Info-/Codequellen |

## Änderungsregel

Reine Aufräumarbeiten dürfen keine stabilen Importpfade oder historischen Nachweise ohne fachlichen Grund brechen. Vor Verschiebungen oder Umbenennungen werden Referenzen ermittelt; danach wird nur der betroffene Scope validiert.
