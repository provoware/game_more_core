# AGENTS.md – BUNKERFREQUENZ

## Ziel

Dieses Repository wird sparsam, modular und nachvollziehbar weiterentwickelt. Jede Änderung braucht einen fachlichen Grund, eine zuständige Zielstelle und einen überprüfbaren Abschluss.

## Verbindlicher Workflow

1. Ziel und Abnahmekriterium der Iteration festlegen.
2. Betroffene Module, Dateien und direkten Verträge ermitteln.
3. Bestehende Zielstelle lesen, bevor neuer Code oder eine neue Datei entsteht.
4. Scope, Grund, Risiken und bewusste Nicht-Ziele festhalten.
5. Kleinste saubere Änderung an der zuständigen Stelle umsetzen; keine Parallelimplementierung erzeugen.
6. Nebenbefunde nur bei unmittelbarer Blockade beheben, sonst als nächste Aufgabe in `TODO.md` aufnehmen.
7. Nur die für den Scope relevanten Tests und Validatoren ausführen.
8. Diff gegen den Plan prüfen; Format- oder Dokumentänderungen ohne fachlichen Grund entfernen.
9. README/TODO/Status/Manifest nur aktualisieren, wenn sich der dort beschriebene Zustand wirklich ändert.
10. CHANGELOG bei fachlicher oder verbindlicher Prozessänderung aktualisieren.
11. Version nur erhöhen, wenn eine neue freigegebene Entwicklungsstufe entsteht.
12. Erst committen und mergen, wenn der geplante Scope und seine Nachweise zusammenpassen.

## Pflichtangaben je Iteration

- **Ziel:** gewünschter Zustand in einem Satz.
- **Abnahme:** beobachtbares Ergebnis für den Abschluss.
- **Scope:** konkrete Dateien/Funktionen/Dokumentblöcke.
- **Grund:** warum genau diese Stelle geändert wird.
- **Risiken:** mögliche Regressionen oder Vertragsfolgen.
- **Nicht-Ziele:** bewusst unveränderte Bereiche.
- **Prüfung:** genau die Kommandos/CI-Gates, die den Scope absichern.

Ändert sich der Scope, wird der Plan vor dem nächsten Patch angepasst. Ohne neuen Befund wird eine Prüfung nicht wiederholt.

## PR- und Merge-Disziplin

- Pro fachlichem Modul gibt es höchstens **einen aktiven Implementierungs-PR**. Alternative Parallel-PRs werden nicht gleichzeitig weitergeführt.
- Ein neuer PR darf keinen bereits offenen PR mit derselben Zielstelle still duplizieren.
- Überholte oder konkurrierende PRs werden geschlossen; erhaltene Ideen werden vorher in `TODO.md` konsolidiert.
- Ein PR mit fehlgeschlagenem relevantem CI-Gate wird **nicht gemergt**.
- Ein grüner lokaler Test ersetzt keinen roten oder fehlenden Remote-Nachweis, wenn für den Scope ein Remote-Gate existiert.
- Nach einer Inhaltsänderung am geprüften Code ist der dazugehörige Gate erneut erforderlich.
- Merge-Entscheidungen beziehen sich auf den tatsächlich geprüften Head-SHA.

## Reproduzierbare Updates

- Befehle laufen vom Repository-Root und werden im Abschluss wörtlich dokumentiert.
- Zufällige oder zeitabhängige Prüfungen verwenden festen Seed bzw. dokumentierten Zeitanker.
- Generierte Dateien nennen Quelle, Parameter und Erzeugungsbefehl.
- Abnahmeberichte unterscheiden lokale Prüfung, Remote-CI und ausstehende Nachweise eindeutig.
- Ein erfolgreicher Lauf wird nicht behauptet, wenn Umgebung oder Netzwerk ihn verhindert haben.
- Commits enthalten nur den geplanten Scope und eine fachlich eindeutige Nachricht.

## Informationshierarchie

Bei Widersprüchen gilt:

1. Architektur-/Fachvertrag für Verhalten und Grenzen.
2. Manifest/Schema für katalogisierte Werte und Datenformen.
3. Runtime + Tests für die Implementierung dieser Verträge.
4. `PROJEKTSTATUS.json` für aktuellen Entwicklungszustand.
5. `TODO.md` für nächste Arbeitseinheiten.
6. README/Index als Navigation, nicht als zweite Fachregel.
7. CHANGELOG als historische Änderungsspur.

`VERSION.json` bezeichnet die letzte versionierte Produkt-/Runtime-Baseline. Eine laufende nächste Iteration darf in `PROJEKTSTATUS.json` und `TODO.md` weiter sein, ohne die Baseline vorzeitig umzubenennen.

## Architekturgrenzen

- UI darf Domain-Zustand nicht direkt schreiben.
- Economy verändert Character-Zustand nur über definierte Services/Events.
- Sync arbeitet mit IDs, Versionen und Events, nicht mit UI-Objekten.
- Texte gehören nicht in Spiellogik.
- Animationen dürfen Gameplay nie blockieren.
- sichtbare Namen sind keine Identifikatoren.
- bestehende Journal-Ereignisse werden nicht überschrieben.
- Runtime persistiert nur in `manifests/JOURNAL_MANIFEST.json` katalogisierte Eventtypen.
- Domain-Aktionen liefern Ereignisse; dauerhafte Zustandsänderungen laufen über den Persistence Kernel.
- Systemzeit ist keine alleinige Autorität und niemals Zufallsseed.

## Agentenrollen

- **Architektur:** Modulgrenzen, Invarianten, Datenverträge.
- **Character Forge:** Skills, Traits, Progression, Balance.
- **Gameplay:** Spielschleifen, Konsequenzen, Spielspaß.
- **Content:** Story, Dialog, reale Bezüge, Textschlüssel.
- **UI/UX:** intuitive Bedienung, Kontrast, Fokus, Reduced Motion.
- **Persistenz:** Save, Journal, Undo, Recovery, Migration.
- **Sync:** Netzwerk, Konflikte, Offline-Warteschlange.
- **Simulation:** Zeit, Zufall, Wirtschaft.
- **QA:** zielgerichtete Tests, Regression und CI-Status.
- **Release:** Version, Manifeste, Changelog und Nachweise.

## Iterationsabschluss

Der Abschluss enthält:

- aktuellen Stand,
- konkrete technische Änderungen,
- ausgeführte Prüfungen mit Ergebnis,
- bekannte Grenzen,
- **drei nummerierte weiterführende Vorschläge**,
- eine klare Empfehlung mit Auswirkungsstufe auf das Game.

Offene Punkte werden als prüfbare Aufgaben in `TODO.md` formuliert.

## Nicht tun

- keine unnötigen Refactorings
- keine kosmetischen Massenänderungen ohne Nutzen
- keine globalen Prüfungen, wenn eine gezielte Prüfung genügt
- keine hart codierten sichtbaren Texte in Spiellogik
- keine neuen Abhängigkeiten ohne belegten Vorteil
- keine alten Save-/Schema-Versionen still brechen
- keine generierten Nachweise ohne dokumentierten Erzeugungsweg
- keine Vermischung von lokalem PASS und Remote-CI
- keine konkurrierenden Implementierungen derselben kanonischen Datei parallel mergen
- keinen bekannten roten CI-Stand nach `main` übernehmen
