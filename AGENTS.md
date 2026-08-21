# AGENTS.md – BUNKERFREQUENZ

## Ziel

Dieses Repository wird sparsam, modular und nachvollziehbar weiterentwickelt. Jede Änderung muss einen fachlichen Grund haben.

## Verbindlicher Workflow

Jede Iteration besteht aus genau einer geplanten Änderungseinheit. Vor dem ersten Patch wird ein Arbeitsplan festgehalten; ungeplante Nebenbefunde werden nicht mitbearbeitet.

1. Anforderung, fachliches Ziel und Abnahmekriterium bestimmen.
2. Betroffene Module, Dateien und konkrete Zeilen oder Blöcke ermitteln.
3. Bestehende Zielstellen und ihre direkten Verträge vor der Änderung lesen.
4. Patchgrund, Risiken, Abhängigkeiten und bewusste Nicht-Änderungen festhalten.
5. Eine geordnete Schrittliste mit höchstens einem aktiven Schritt erstellen.
6. Kleinste saubere Änderung an der vorhandenen Stelle umsetzen; keine Parallelimplementierung erzeugen.
7. Nebenbefunde nur bei unmittelbarer Blockade beheben, sonst als nächste Iteration in `TODO.md` eintragen.
8. Nach dem letzten Patch genau die betroffenen Ausgaben, Verträge und Tests validieren.
9. README/TODO nur bei einer echten Status- oder Ablaufänderung aktualisieren.
10. CHANGELOG bei fachlicher oder verbindlicher Prozessänderung aktualisieren.
11. Version nur erhöhen, wenn der Änderungsumfang dies rechtfertigt.
12. Diff, Arbeitsbaum und Änderungsprotokoll vor dem Commit gegen den Plan prüfen.

## Pflichtangaben je Iteration

Der Plan muss vor der Änderung knapp und prüfbar benennen:

- **Ziel:** gewünschter fachlicher Zustand in einem Satz.
- **Abnahme:** beobachtbares Ergebnis, das den Abschluss belegt.
- **Scope:** betroffene Dateien sowie Zeilen, Funktionen oder Dokumentblöcke.
- **Grund:** warum der Eingriff nötig ist und warum die gewählte Stelle zuständig ist.
- **Risiken:** mögliche Regressionen, Daten- oder Vertragsfolgen.
- **Nicht-Ziele:** bewusst unveränderte Bereiche.
- **Schritte:** Analyse, Patch, einmalige Endvalidierung, Diff-Prüfung und Abschluss.

Ändert sich der Scope während der Arbeit, wird der Plan vor einem weiteren Patch aktualisiert. Ohne neuen Befund wird keine Prüfung wiederholt.

## Reproduzierbare Updates

- Befehle werden vom Repository-Root ausgeführt und im Abschluss wörtlich dokumentiert.
- Zufällige oder zeitabhängige Prüfungen verwenden einen festen Seed beziehungsweise einen dokumentierten Zeitanker.
- Generierte Dateien nennen Quellstand, Parameter und Erzeugungsbefehl; volatile Daten werden nicht ohne fachlichen Grund versioniert.
- Abnahmeberichte unterscheiden lokale Prüfung, Remote-CI und noch ausstehende Nachweise eindeutig.
- Ein erfolgreicher Lauf wird nicht behauptet, wenn Abhängigkeiten, Netzwerk oder Umgebung ihn verhindert haben.
- Prüfungsergebnisse müssen dem tatsächlich gepatchten Stand entstammen; nach der Endvalidierung folgt keine Inhaltsänderung ohne neue Validierung.
- Commits enthalten nur den geplanten Scope und erhalten eine fachlich eindeutige Nachricht.

## Iterationsabschluss

Der Abschluss enthält ein kompaktes Änderungsprotokoll, die relevanten Prüfkommandos mit Ergebnis, bekannte Grenzen und genau zwei konstruktive Empfehlungen für die nächste Iteration. Offene Punkte werden als prüfbare Aufgaben in `TODO.md` formuliert.

## Architekturgrenzen

- UI darf Domain-Zustand nicht direkt schreiben.
- Economy verändert Character-Zustand nur über definierte Services/Events.
- Sync arbeitet mit IDs, Versionen und Events, nicht mit UI-Objekten.
- Texte gehören nicht in Spiellogik.
- Animationen dürfen Gameplay nie blockieren.
- sichtbare Namen sind keine Identifikatoren.
- bestehende Journal-Ereignisse werden nicht überschrieben.
- Runtime-Code darf nur Journal-Eventtypen persistieren, die in `manifests/JOURNAL_MANIFEST.json` katalogisiert sind.
- Domain-Aktionen liefern Ereignisse; dauerhafte Zustandsänderungen laufen über den Persistence Kernel.
- Systemzeit ist keine alleinige Autorität und niemals Zufallsseed.

## Agentenrollen

- Architektur: Modulgrenzen, Invarianten, Datenverträge.
- Character Forge: Skills, Traits, Progression, Balance.
- Gameplay: Spielschleifen, Konsequenzen, Spielspaß.
- Content: Story, Dialog, reale Bezüge, Textschlüssel.
- UI/UX: intuitive Bedienung, Kontrast, Fokus.
- Persistenz: Save, Journal, Undo, Recovery, Migration.
- Sync: Netzwerk, Konflikte, Offline-Warteschlange.
- Simulation: Zeit, Zufall, Wirtschaft.
- QA: zielgerichtete Tests und Regression.
- Release: Version, Manifeste, Changelog, Nachweise.

## Nicht tun

- keine unnötigen Refactorings
- keine kosmetischen Massenänderungen ohne Nutzen
- keine globalen Prüfungen, wenn eine gezielte Prüfung genügt
- keine hart codierten sichtbaren Texte in Spiellogik
- keine neuen Abhängigkeiten ohne klaren Vorteil
- keine alten Save-/Schema-Versionen still brechen
- keine generierten Nachweise ohne dokumentierten Erzeugungsweg
- keine Vermischung von lokal bestandener Prüfung und Remote-CI-Status
