# Entwicklerhandbuch – Foundation

## Einstieg

1. `README.md` lesen.
2. `TODO.md` auf aktuelle Iteration prüfen.
3. `docs/ARCHITEKTURVERTRAG.md` lesen.
4. Betroffenes Manifest und Schema lesen.
5. Nur die konkrete Zielstelle ändern.
6. Passende gezielte Validierung ausführen.
7. README/TODO/CHANGELOG nur dann aktualisieren, wenn sich deren Inhalt tatsächlich ändert.

## Versionierung

Aktueller Vor-Code-Stand nutzt SemVer-ähnliche Entwicklungsstände:
`0.4.0-alpha.1`

- Patch/Alpha-Revision: kleine kompatible Foundation-Korrektur.
- Minor innerhalb 0.x: neue Entwicklungsstufe/Systemvertrag.
- Breaking Schemaänderung: Migration und dokumentierte Schema-Version.

## Definition of Done für eine Foundation-Änderung

- fachlicher Grund dokumentierbar
- keine unnötige Nebenänderung
- JSON/Schema syntaktisch valide
- IDs eindeutig
- referenzierte Dateien vorhanden
- relevante Invarianten nicht verletzt
- README/TODO korrekt
- CHANGELOG korrekt
- Version/Status konsistent

## Prüfstrategie

Nicht „alles immer testen“, sondern risikobasiert:
- Content-Änderung → Content/Schema/ID-Prüfung
- Progression → Character-/Balance-Prüfung
- Persistenz → Save/Journal/Recovery-Prüfung
- Sync → Sync-/Konfliktprüfung
- UI → UI-/Accessibility-Smoke-Test

Globale Regression erst, wenn eine Änderung mehrere Bereiche berührt oder ein Release-Gate erreicht ist.
