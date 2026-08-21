# Architekturvertrag 0.4

## Ziel

Der Kern bleibt erweiterbar, testbar und unabhängig von UI, Telegram, konkreter Speicherung und Content-Dateien.

## Ebenen

1. **Domain** – Spielregeln und Zustände.
2. **Application** – Commands, Queries, Workflows und Validatoren.
3. **Infrastructure** – Persistenz, Journal, Clock, Sync, Datenbank.
4. **Presentation** – UI, HUD, Animation, Audio und Accessibility.
5. **Content** – Texte, Figuren, Traits, Missionen, Orte und reale Bezüge.

## Invarianten

1. Story definiert keine Startfähigkeit.
2. Alle 11 Startfiguren teilen dieselbe Startwertdefinition.
3. Sichtbare Namen/Aliase sind editierbar; technische IDs bleiben stabil.
4. UI schreibt Domain-Zustand ausschließlich über Application-Commands.
5. Journal ist append-only.
6. Undo wird als Gegenereignis modelliert.
7. Snapshots ersetzen das Journal nicht.
8. Systemzeit darf allein keine irreversible Aktion auslösen.
9. Serverbestätigte gemeinsame Transaktionen sind bei Sync autoritativ.
10. Fehler in Animation, Audio, Ranking oder Netzwerk dürfen lokales Kern-Gameplay nicht stoppen.
11. sichtbare Texte werden über Textschlüssel geladen.
12. Schemaänderungen benötigen Migration oder explizite Inkompatibilitätsentscheidung.

## Vorgesehene Modulstruktur

```text
src/
  domain/
    characters skills traits progression biography crew relationships training
    missions world locations events clubs inventory economy market ranking time
  application/
    commands queries workflows validators services
  infrastructure/
    persistence journal snapshots recovery clock sync telegram database logging
  presentation/
    ui hud screens animations cutscenes audio accessibility
content/
schemas/
manifests/
migrations/
tests/
tools/
```

Leere Implementierungsordner werden erst angelegt, wenn tatsächlicher Code entsteht. Git-Struktur soll keine nutzlosen Platzhalterdateien enthalten.

## Änderungsregel

Vor jeder Änderung:
- Zielstelle bestimmen
- kleinsten sinnvollen Scope festlegen
- relevante Verträge prüfen

Nach jeder Änderung:
- nur relevante Validierung
- README/TODO bei Statusänderung
- CHANGELOG bei fachlicher Änderung
- Versionierung gemäß Umfang
