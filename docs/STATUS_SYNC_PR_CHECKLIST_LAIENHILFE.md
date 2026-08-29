# Status-Sync PR-Checkliste – Laienhilfe

## Wozu ist das gut?

Wenn `Status Sync` rot wird, hängen `TODO.md`, `FEATURE_POOL.md` oder `PROJEKTSTATUS.json` hinter einem bereits sicher gemergten Stand zurück. Der vorhandene Checker bleibt absichtlich rein lesend und schreibt nichts automatisch nach `main`.

Neu kann er eine direkt kopierbare Markdown-Checkliste erzeugen:

```bash
python3 tools/status_sync.py suggest-markdown
```

Die Ausgabe nennt exakt:

- den erkannten letzten fachlich relevanten Safe-Merge,
- den neuen Anker für `TODO.md`,
- den neuen Anker für `FEATURE_POOL.md`,
- die beiden zu ändernden `status_sync`-Felder in `PROJEKTSTATUS.json`,
- die Regel, `remote_validation` nicht umzudeuten,
- den abschließenden `STATUS SYNC PASS`-Nachweis,
- die Pflicht, erst mit grünen Required Gates über `/safe-merge` zu mergen.

## Was macht der Befehl ausdrücklich nicht?

`suggest-markdown` schreibt keine Datei, verändert keinen Branch und aktualisiert `main` nicht. Er erzeugt nur eine eindeutige Reparaturcheckliste. Damit bleiben die drei vorhandenen Statusdateien die einzigen kanonischen Statusquellen.

## Warum ist `remote_validation` tabu?

Der Status-Sync-Anker sagt: **Bis zu welchem fachlich relevanten Safe Merge ist die Projektübersicht nachgezogen?**

`remote_validation` sagt dagegen: **Welcher konkrete PR hat eine bestimmte Abnahme tatsächlich bewiesen?**

Diese historische Evidenz darf nicht auf einen neueren PR umgeschrieben werden, nur weil der Status-Anker weitergezogen wird.

## Warum wird ein reiner Status-Sync-PR übersprungen?

Ein Status-Sync repariert nur die Projektübersicht und fügt dem Spiel keine neue fachliche Stufe hinzu. Würde sein eigener Merge sofort zum nächsten Anker, müsste direkt danach wieder ein weiterer Status-Sync folgen. Deshalb zeigt der Anker immer auf den letzten **fachlich relevanten** Safe Merge; reine Statuskorrekturen werden bewusst übersprungen.

## Praktischer Ablauf

1. `python3 tools/status_sync.py check` zeigt den Drift.
2. `python3 tools/status_sync.py suggest-markdown` erzeugt die Reparaturcheckliste.
3. Nur die dort genannten Ankerwerte in den drei kanonischen Dateien aktualisieren.
4. `remote_validation` unverändert lassen.
5. `python3 tools/status_sync.py check` erneut ausführen.
6. Required Gates auf dem finalen PR-Head abwarten.
7. Bei vollständig grünem Stand ausschließlich `/safe-merge` verwenden.

## Merksatz

**Die Checkliste hilft beim sicheren Nachziehen der Projektwahrheit; sie ersetzt weder Prüfung noch Safe Merge.**

## Spätere Verbesserungsidee

Eine spätere rein diagnostische Erweiterung könnte zusätzlich die Anzahl der fachlich relevanten Safe Merges zwischen altem und erwartetem Anker **und die beschreibende `anchor_iteration` des Ziel-PRs** ausgeben. Nutzen: Man erkennt sofort, wie alt ein Drift ist, und reduziert manuelle Abweichungen zwischen Merge-Anker und Iterationsbezeichnung, ohne Dateien automatisch zu verändern.
