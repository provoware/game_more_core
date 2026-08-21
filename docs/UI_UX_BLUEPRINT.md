# Character Forge UI/UX Blueprint 0.4.3

## Designrichtung
Verbindliche Basis bleibt **Industrial Brutalist – Variante A**: schwarzer Beton, Anthrazit, Stahl, Signalrot, klare technische Typografie, große Flächen und wenige, funktionale Akzentfarben.

## Kanonische visuelle Übersicht

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

Die Übersicht dient als gemeinsame visuelle Referenz für Persistence, die vier Character-Forge-Varianten und den Gameplay Action Contract. Bei Widersprüchen gelten die Text- und Manifestverträge; die Grafik ist bewusst übersichtlich und nicht selbst die Datenquelle.

## Vier Entwurfsvarianten
### A1 – CONTROL ROOM
Crew links, Charakter/3D-Portrait und zentrale Werte in der Mitte, aktueller Kontext rechts, Journal/Status unten. Beste Gesamtübersicht für Desktop.

### A2 – COMPACT GRID
Kompakte modulare Karten, Skillmatrix und aufklappbare Panels. Hohe Informationsdichte für Spieler, die schnell vergleichen und verwalten wollen.

### A3 – CINEMATIC FORGE
Große Charakterinszenierung, radialer Skill-/Trait-Baum, kontextabhängige Drawer. Visuell stärkste Variante für Identität, Level-Up und Biografie.

### A4 – OPS DECK
Vertikale Workflow-Schiene links, große aktuelle Aktion in der Mitte, Live-Status rechts. Stärkste Laienführung: immer sichtbar, was jetzt wichtig ist.

## Gemeinsamer Workflow
`AKTUELLES ZIEL → NÄCHSTE AKTION → ERGEBNIS → ENTWICKLUNG → NÄCHSTES ZIEL`

Maximal drei primäre Aktionen gleichzeitig. Die wichtigste Aktion erhält stärksten Kontrast, Rahmen, Icon und Klartext.

## Character Overview
Avatar, editierbarer Name/Alias, Motto, Leveltitel, Level/Resonanz, drei stärkste Skills, aktive Traits, aktuelle Tendenz/Spezialisierung, Energie/Stress/Ruf und letzte Biografie-Meilensteine.

## Skills & Traits
Skills werden immer als Zahl + Balken + Trend + Rang angezeigt. Traits zeigen Stufe I–V, Fortschritt zur nächsten Stufe, positive Wirkung und Konsequenz. Verdeckte Traits zeigen nur sinnvolle Hinweise, keine Prozent-Geheimzahlen.

## Dynamische Biografie
Chronikfilter: Meilensteine, Story, Skills, Traits, Crew, Events, Clubs, Funde. Einträge werden aus validierten Journalereignissen erzeugt, nicht frei aus UI-Zustand.

## Ranking / Network
Standard: Top 10; `ALLE ANZEIGEN` öffnet unbegrenzte Liste. Sortierung nach Gesamtlevel, Skill, Ruf, Events, Clubs, Vermögen, Entdeckungen, Traits oder Resonanz. Sync-Status immer mit Farbe + Symbol + Text.

## Level-/Skill-Up
Animationen sind kurz, überspringbar und niemals blockierend. Reduced-Motion zeigt statische Karten. Keine stroboskopartigen Effekte; das eigentliche Game-Event ist bereits vor der Animation committed.

## Kontrast
- Signalrot = primäre Aktion / kritischer Kontext
- Gelb = Aufmerksamkeit / noch offen
- Grün = bestätigt / erfolgreich
- Cyan = Information / Netzwerk
- Weiß = aktiver Inhalt
- Grau = sekundär / deaktiviert

Farbe ist niemals alleinige Information; zusätzlich Icon, Text und Form.

## Bedienbarkeit
- bevorzugte Grundschrift 18 px, niemals unter 16 px
- Interaktionsziel mindestens 44 px
- 3 px sichtbarer Tastaturfokus
- vollständige Tastaturnavigation
- Screenreader-Labels
- High-Contrast und Reduced-Motion
- wichtige Aktion bleibt bei schmalen Layouts sichtbar

## Textauslagerung
Alle sichtbaren Texte werden über `content/de/ui/character_forge.json` referenziert. Kein sichtbarer UI-Text wird in Spiellogik hart codiert.

## Empfehlung innerhalb der vier Varianten
A4 Ops Deck für den normalen Spielworkflow; A3 Cinematic Forge für Charakter-/Levelansichten. Beide dürfen dieselben Komponenten teilen, damit kein zweites UI-System entsteht.
