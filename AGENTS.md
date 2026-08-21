# AGENTS.md – BUNKERFREQUENZ

## Ziel

Dieses Repository wird sparsam, modular und nachvollziehbar weiterentwickelt. Jede Änderung muss einen fachlichen Grund haben.

## Verbindlicher Workflow

1. Anforderung und betroffene Module bestimmen.
2. Bestehende Stelle vor Änderung lesen.
3. Kleinste saubere Änderung wählen.
4. Keine Parallelimplementierung erzeugen, wenn eine vorhandene Stelle erweitert werden kann.
5. Nur die für die Änderung relevanten Prüfungen ausführen.
6. Fehlerursache beheben, nicht Symptome verteilen.
7. README/TODO bei Statusänderung aktualisieren.
8. CHANGELOG bei fachlicher Änderung aktualisieren.
9. Version nur erhöhen, wenn der Änderungsumfang dies rechtfertigt.
10. Nach Änderung den tatsächlich betroffenen Stand validieren.

## Architekturgrenzen

- UI darf Domain-Zustand nicht direkt schreiben.
- Economy verändert Character-Zustand nur über definierte Services/Events.
- Sync arbeitet mit IDs, Versionen und Events, nicht mit UI-Objekten.
- Texte gehören nicht in Spiellogik.
- Animationen dürfen Gameplay nie blockieren.
- sichtbare Namen sind keine Identifikatoren.
- bestehende Journal-Ereignisse werden nicht überschrieben.
- Systemzeit ist keine alleinige Autorität.

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
