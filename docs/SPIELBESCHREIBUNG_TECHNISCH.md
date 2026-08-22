# BUNKERFREQUENZ – Technische Spielbeschreibung

> **Zielgruppe:** Softwareentwicklerinnen und Softwareentwickler, technische Designer, Architektinnen, QA, Build-/Release-Verantwortliche und externe Teams, die das Spiel sicher erweitern oder integrieren sollen.
>
> **Geltung:** Dieses Dokument erklärt den technischen Gesamtzusammenhang. Bei Abweichungen haben der jeweilige Fachvertrag, Manifeste und Schemas, Runtime und Tests sowie der kanonische Projektstatus in dieser Reihenfolge Vorrang.

## 1. Systemüberblick

BUNKERFREQUENZ ist ein ereignisbasiertes Crew-Rollenspiel mit deterministischer Charakterprogression, journalfähigem Eventzustand, transaktionaler Equipment-/Economy-Logik und mehreren schreibgeschützten Präsentationen.

Der Kern ist bewusst **headless** (ohne verpflichtende grafische Oberfläche) und verwendet aktuell ausschließlich die Python-Standardbibliothek. Die Spiellogik ist von UI, Netzwerktransport, konkreten Texten und Dateispeicherung getrennt.

```text
Content + Manifeste + Schemas
             │
             ▼
Presentation ──► Application ──► Domain
     ▲                │             │
     │                ▼             ▼
     └──────── Projektionen    Domain-Ereignisse
                      │             │
                      └──────► Persistence Kernel
                                     │
                       ┌─────────────┼─────────────┐
                       ▼             ▼             ▼
                    Journal        State        Snapshots
```

## 2. Technisches Produktziel

Das System soll einen durchgängigen Ablauf ermöglichen:

```text
Command
→ Voraussetzungen und Revision prüfen
→ deterministisches Domain-Ergebnis berechnen
→ katalogisierte Ereignisse erzeugen
→ Ereignisse dauerhaft journalisieren
→ abgeleiteten Zustand atomar aktualisieren
→ bestätigten Zustand projizieren
→ nach Neustart identisch rekonstruieren
```

Die Architektur optimiert auf vier Eigenschaften:

1. **Nachvollziehbarkeit:** Jede dauerhafte Änderung besitzt eine fachliche Ursache.
2. **Wiederholbarkeit:** Explizite Seeds, IDs und Revisionen verhindern zeitabhängige Abweichungen.
3. **Fehlertoleranz:** Journal, Snapshot und Recovery können einen bestätigten Stand rekonstruieren.
4. **Austauschbare Darstellung:** A4, A3 und spätere Clients verwenden dieselben bestätigten Daten.

## 3. Aktueller Reifegrad

| Ebene | Stand |
|---|---|
| Release-Baseline | `0.5.2-alpha.1` |
| Letzte remote validierte Feature-Stufe | `0.8.1 – Event State Foundation` |
| Aktive Iteration | `0.8.2 – Equipment & Economy` |
| 0.8.2 | implementiert; lokale und Remote-Gesamtabnahme des Vertical Slice noch offen |
| Nächster Produktblock | `0.8.3 – vollständiger Event-Loop` |
| Grafischer Client | statischer, schreibgeschützter HTML-Blueprint; kein Game-Client |
| Netzwerk/Telegram | geplant, nicht implementiert |

Die Produktversion und die aktive Feature-Iteration sind absichtlich getrennt. `VERSION.json` beschreibt die letzte freigegebene Runtime-Baseline; `PROJEKTSTATUS.json` und `TODO.md` beschreiben die laufende Entwicklung.

## 4. Architektur und Verantwortlichkeiten

### 4.1 Domain

Die Domain enthält Regeln und Zustände ohne UI- oder Dateisystemzugriff.

Aktuelle Kernmodule:

- `domain/character.py`: Character-Zustand und grundlegende Validierung,
- `domain/progression.py`: Progressionszustände und Stufen,
- `domain/trait_effects.py`: begrenzte Trait-Wirkungen und Soft-Konflikte,
- `domain/event.py`: Eventzustand, Planungsdaten, Revision und Phasenmaschine,
- `domain/economy.py`: Katalog, Inventar, Reservierung, Ledger und Preisregeln.

Domain-Aktionen liefern Ereignisse oder geprüfte Folgezustände. Sie persistieren nicht selbst.

### 4.2 Application

Die Application-Schicht koordiniert Use Cases (Anwendungsfälle), Commands und Services.

Wichtige Verantwortungen:

- Command-Routing und Capability-Prüfung,
- Action Resolution,
- Character- und Economy-Transaktionen,
- Character-Forge-Session,
- Recovery-Orchestrierung,
- Ableitung bestätigter Presentation-Ereignisse.

Die UI darf ausschließlich über diese Schicht Schreibabsichten senden.

### 4.3 Infrastructure

Die Infrastructure-Schicht implementiert die dauerhafte Speicherung:

- append-only Journal,
- Hashkette,
- atomare State- und Metadatenwrites,
- Snapshots,
- Replay und Recovery,
- Idempotenzregistrierung.

Die Implementierung liegt zentral in `infrastructure/persistence.py`. Neue Module dürfen keinen zweiten Speicherweg neben diesem Kernel etablieren.

### 4.4 Presentation

Presentation erzeugt schreibgeschützte View-Modelle (für Ansichten aufbereitete Daten) und Command-Entwürfe.

Aktuelle Bereiche:

- gemeinsame Komponenten,
- Character-Projektion,
- Biografieprojektion,
- Action-Auswahl,
- A4 Ops Deck,
- A3 Cinematic Forge,
- Ranking-/Network-Grundlage,
- lokaler, nicht persistenter Presentation-State,
- Feedback aus bestätigten Ereignissen.

Eine Projektion darf fehlende Daten nicht erfinden. Unbestätigte Werte bleiben unbekannt oder sichtbar nicht bestätigt.

### 4.5 Content

Sichtbare Texte liegen unter `content/de/` und werden über stabile Textschlüssel referenziert. Spiellogik enthält keine hart codierten sichtbaren Texte.

### 4.6 Verträge und Kataloge

- `docs/`: lesbare Fach- und Architekturverträge,
- `manifests/`: katalogisierte Werte, IDs, Eventtypen und Fähigkeiten,
- `schemas/`: maschinenlesbare Datenformen,
- `tests/`: ausführbare Vertrags- und Regressionstests.

## 5. Zentrale Invarianten

1. Alle elf Startfiguren verwenden dieselbe Startwertdefinition.
2. Sichtbare Namen sind änderbar und niemals Identifikatoren.
3. UI und Presentation schreiben Domain-Zustand nicht direkt.
4. Dauerhafte Zustandsänderungen laufen über den Persistence Kernel.
5. Nur katalogisierte Journal-Ereignistypen dürfen persistiert werden.
6. Bestehende Journal-Ereignisse werden niemals überschrieben.
7. Undo oder fachliche Korrektur erfolgt durch Kompensation.
8. Snapshots beschleunigen Recovery, ersetzen das Journal jedoch nicht.
9. Systemzeit ist keine alleinige Autorität und kein Zufallsseed.
10. Animation, Audio, Ranking und Netzwerk dürfen lokales Kern-Gameplay nicht blockieren.
11. Economy verändert Eventbudget und Inventar atomar.
12. Character-, Event- und Economy-State-Blöcke müssen beim Schreiben einander erhalten.

## 6. Aggregierter Spielzustand

Der persistierte Spielstand besteht aus koexistierenden fachlichen Blöcken:

```json
{
  "character": { "...": "Character-Zustand" },
  "event": { "...": "Event-Zustand" },
  "economy": { "...": "Katalog, Inventar und Ledger" }
}
```

Der Ausschnitt ist absichtlich schematisch. Verbindliche Felder stehen in den jeweiligen Schemas und Manifesten.

Wichtig ist der Write-Merge-Vertrag: Eine Character-Transaktion darf `event` oder `economy` nicht entfernen; eine Event- oder Economy-Transaktion darf den Character-Block nicht ersetzen.

## 7. Character-System

### 7.1 Identität und Profil

Die technische Character-ID bleibt stabil. Sichtbare Namen, Alias, Spitznamen und Motto sind Profilwerte und dürfen geändert werden, ohne Referenzen zu brechen.

### 7.2 Startzustand

- 16 Skills starten bei `10`,
- Level startet bei `1`,
- Gesamt-XP startet bei `0`,
- Energie startet bei `100`,
- Stress und Ruf starten bei `0`.

Narrative Herkunft erzeugt keine Startboni.

### 7.3 Action Resolution

Der Resolver erhält mindestens:

- eine Action-Definition,
- den aktuellen Character-Zustand,
- eine eindeutige Action-Instanz,
- einen expliziten Seed,
- die erforderlichen Voraussetzungen.

Er prüft die Action, berechnet deterministisch Qualität und Folgen und erzeugt Domain-Ereignisse. Energie und Stress werden auf `0–100` begrenzt.

### 7.4 Skillprogression

Die fachliche Grundformel lautet:

```text
Skill-XP = Basis-XP × Schwierigkeit × Qualität × Neuheit
           × Erschöpfung × Wiederholung × Quellenfaktor
           × Trainingswirkung
```

Die exakten Faktoren und Grenzen kommen aus Manifesten. Produktcode soll diese Katalogwerte nicht duplizieren.

### 7.5 Traitprogression

Traits sammeln Evidenz aus kategorisierten Quellen. Training zählt schwächer als Praxis, Krisen und Teamarbeit. Stufen benötigen Schwellenwerte, Mindestlevel, Ereigniszahlen und bei hohen Stufen mehrere Quellen.

Soft-Konflikte dämpfen positive Wirkungen, löschen aber keine Traits. Positive und negative Modifikatoren besitzen globale Kappen.

### 7.6 Spezialisierung, Level und Resonanz

Spezialisierungen werden aus dauerhaftem Skill-Vorsprung abgeleitet. Der Character erreicht regulär Level 50; danach verwendet die Progression offene Resonanzränge.

### 7.7 Biografie

Die Biografieprojektion verarbeitet ausschließlich validierte Journal-Ereignisse. Text wird über Textschlüssel erzeugt. Freitext aus unbestätigten Zuständen darf keine kanonische Biografie werden.

## 8. Event-System

### 8.1 EventState

Der Eventzustand besitzt:

- `event_id`,
- Anzeigename,
- Ort und Zugangsstatus,
- Budgetrahmen in Cent,
- Acts,
- Crew-Zuordnungen,
- Equipmentanforderungen,
- Zeitfenster mit UTC-Offset und Zeitzone,
- Sicherheitsstatus,
- Phase,
- monotone Revision.

### 8.2 Phasenmaschine

```text
draft
  → planning
  → procurement
  → transport
  → setup
  → soundcheck
  → live ↔ crisis
  → teardown
  → settlement
  → completed
```

Ungültige Sprünge werden abgelehnt. Ab `transport` gelten Ort, verifizierter Zugang, gültiges Zeitfenster und `safety_status=cleared` als Gate.

### 8.3 Revisionskontrolle

Jeder schreibende Event-Command bezieht sich auf eine erwartete Revision. Ist sie veraltet, wird der Write fail-closed (sicher abgelehnt). Dadurch überschreibt ein alter Clientstand keine neuere Planung.

### 8.4 Event-Ereignisse

Die Foundation persistiert:

- `event.created`,
- `event.planning_updated`,
- `event.phase_changed`.

Neue Eventtypen müssen zuerst im Journalmanifest katalogisiert und anschließend durch Domain, Persistence, Recovery und Tests geführt werden.

## 9. Equipment- und Economy-System

### 9.1 Zustandsmodell

Der Economy-Block trennt:

| Teil | Verantwortung |
|---|---|
| `catalog` | unverwechselbare Equipmentdefinitionen und Preisdaten |
| `inventory` | bestätigter Besitz und reservierte Menge |
| `ledger` | unveränderliche Folge bestätigter Operationen |
| `market_tick` | deterministische Preisstufe |
| `revision` | monotone Economy-Version |

### 9.2 Preismodell

Der Preis wird aus Grundpreis, katalogisierter Schwankung in Basispunkten und `market_tick` berechnet. Systemzeit und impliziter Zufall sind ausgeschlossen.

Damit gilt:

```text
gleicher Katalog + gleicher market_tick = gleicher Stückpreis
```

### 9.3 Transaktionale Invarianten

- Kaufen erhöht Inventar und senkt Eventbudget gemeinsam.
- Verkaufen senkt freien Besitz und erhöht Budget gemeinsam.
- Reservierter Bestand darf weder verkauft noch verbraucht werden.
- Bestand, Reservierung und Budget werden niemals negativ.
- Verbrauch ist nur für katalogisierte verbrauchbare Güter erlaubt.
- Eine Anforderung ist erst bei vollständig reservierter Menge `ready`.

### 9.4 Idempotenz

Eine Command-ID bezeichnet genau einen fachlichen Inhalt:

- gleiche ID + gleicher Inhalt: folgenloser Replay,
- gleiche ID + anderer Inhalt: Konflikt und Ablehnung.

Diese Regel verhindert doppelte Käufe oder Verkäufe nach Wiederholung eines Requests.

### 9.5 Kompensation

Nur bestätigte Käufe und Verkäufe sind kompensierbar. Die Gegenbuchung verwendet exakt den ursprünglichen Stückpreis, wird höchstens einmal angewendet und validiert den aktuellen Bestand erneut.

### 9.6 Atomarer Event-Folgezustand

`economy.transaction_posted` trägt den bestätigten Economy- und Event-Folgezustand. Dadurch werden Budget und Inventar im Replay nicht auseinandergezogen.

## 10. Command- und Ereignisfluss

### 10.1 Schreibender Standardpfad

```text
1. Presentation erzeugt eine Nutzerabsicht.
2. Application prüft Capability und Command-Form.
3. Service lädt den aktuellen aggregierten Zustand.
4. Domain prüft IDs, Revision, Voraussetzungen und Invarianten.
5. Domain/Service erzeugt katalogisierte Ereignisse und Folgezustand.
6. Persistence prüft Idempotenz, Sequenz und Eventkatalog.
7. Journal wird dauerhaft geschrieben.
8. Abgeleiteter State und Metadaten werden atomar aktualisiert.
9. Application liefert bestätigtes Ergebnis zurück.
10. Presentation projiziert den neuen Zustand und Feedback.
```

### 10.2 Warum Journal zuerst

Wird der Prozess nach dem dauerhaften Journaleintrag, aber vor dem State-Write unterbrochen, kann Recovery den State aus dem Journal wiederherstellen. Würde der State zuerst geschrieben, könnte eine nicht nachvollziehbare Zustandsänderung entstehen.

### 10.3 Idempotente Wiederholung

Application und Persistence müssen Wiederholungen nach Timeout oder Neustart tolerieren. Ein bereits bestätigter identischer Command darf keine zweite fachliche Wirkung erzeugen.

## 11. Persistenz und Recovery

### 11.1 Journal

Das Journal ist append-only und durch eine SHA-256-Hashkette geschützt. Sequenzen und Hashbezüge machen fehlende, vertauschte oder veränderte Einträge erkennbar.

### 11.2 Atomare Writes

State und Metadaten werden so ersetzt, dass eine Datei entweder vollständig oder gar nicht sichtbar wird. Ein Zwischenstand darf nicht als gültiger Save erscheinen.

### 11.3 Snapshots

Snapshots sind geprüfte Wiederanlaufpunkte mit angewandter Sequenz. Sie verkürzen Replay, sind aber keine alternative Wahrheit neben dem Journal.

### 11.4 Autosave

Die Character-Forge-Session erzeugt bei ausstehenden Änderungen nach 60 Sekunden einen zusätzlichen Checkpoint. Fachliche Actions werden bereits bei ihrer Bestätigung dauerhaft persistiert; die Autosave-Frist ist kein Verlustfenster.

### 11.5 Recovery-Ablauf

```text
neuesten gültigen Snapshot suchen
→ Journal ab Snapshot-Sequenz validieren
→ katalogisierte Ereignisse replayen
→ Character/Event/Economy gemeinsam rekonstruieren
→ beschädigten Tail quarantänisieren
→ reparierten State schreiben
→ Recovery-Receipt erzeugen
```

Ein unvollständiger oder checksum-falscher Snapshot wird übersprungen. Existiert kein gültiger Checkpoint, endet Recovery kontrolliert mit einem fachlichen Fehler.

## 12. Presentation und UI-Integration

### 12.1 Capability-Grenze

Presentation erhält explizite Fähigkeiten wie:

- `can_edit_profile`,
- `can_undo_profile`,
- `can_execute_action`.

Ein Client darf nicht aus einem sichtbaren Button ableiten, dass ein Write zulässig ist. Die Capability muss beim Erstellen bzw. Dispatchen des Commands erneut geprüft werden.

### 12.2 Command-Grenze

Aktuelle schreibende Application-Commands umfassen:

- `profile.update`,
- `profile.undo_last`,
- `action.execute`.

Presentation-lokale Commands wie View-Auswahl oder Feedback-Ausblenden sind nicht persistent und verändern keinen Domain-State.

### 12.3 A4 und A3

A4 Ops Deck und A3 Cinematic Forge verwenden gemeinsame Komponenten und dieselben bestätigten Daten. A3 darf Animation und dramaturgische Gewichtung ergänzen, nicht aber Zustand oder Ergebnis verändern.

### 12.4 Reduced Motion

Fortschrittsfeedback besitzt einen Fallback mit reduzierter Bewegung. Gameplay bleibt unabhängig von Animationsstatus und Animationsfehlern bedienbar.

### 12.5 HTML-Blueprint

`web/index.html` ist ein statischer Evaluator für Designreferenz, Workflow und UI-Manifest. Er:

- ist lokal startbar,
- erzeugt einen maschinenlesbaren Prüfbericht,
- schreibt keine Domain-Daten,
- ist kein Ersatz für den späteren A4-Game-Client.

## 13. Content- und Lokalisierungsmodell

Sichtbare Namen und Texte werden über Schlüssel aufgelöst. Die Regeln dafür sind:

- technische IDs bleiben stabil,
- lokalisierte Werte dürfen sich ändern,
- Spiellogik vergleicht keine sichtbaren Namen,
- fehlende Textschlüssel müssen kontrolliert sichtbar werden,
- Content darf keine Startfähigkeiten oder versteckte Domainregeln definieren.

## 14. Determinismus und Zeit

### 14.1 Zufall

Jeder zufallsabhängige Ablauf benötigt einen expliziten Seed. Die Systemzeit darf niemals still als Seed dienen.

### 14.2 Zeitfenster

Eventzeitfenster sind offset-aware ISO-8601-Zeitpunkte. Das Ende muss nach dem Start liegen. Zeitzoneninformation gehört zum fachlichen Zustand.

### 14.3 Marktzeit

Der Economy-Markt verwendet `market_tick` statt Wandzeit. Ein Tick ist ein bestätigter fachlicher Zustand, kein impliziter Blick auf die lokale Uhr.

### 14.4 Reproduzierbare Tests

Simulationen und zeitabhängige Checks verwenden feste Seeds oder dokumentierte Zeitanker. Generierte Berichte nennen Quelle, Parameter und Befehl.

## 15. Fehlerstrategie

### 15.1 Fail-closed

Bei unklarer Autorität, unbekannter Revision, unvollständiger Voraussetzung oder widersprüchlicher ID wird der schreibende Vorgang abgelehnt. Das System errät keinen gültigen Zustand.

### 15.2 Fachliche Fehlermeldung

An der UI-Grenze wird der Fehler in einfacher Sprache erklärt. Technische Details dürfen separat protokolliert werden.

Beispiele:

- „Die Eventplanung wurde inzwischen geändert. Lade den aktuellen Stand und prüfe deine Eingabe erneut.“
- „Das Equipment ist für dieses Event reserviert und kann nicht verkauft werden.“
- „Der letzte sichere Zustand wurde wiederhergestellt. Die Aktion wurde nicht doppelt übernommen.“

### 15.3 Keine Teilwirkung

Ein Fehler in einer Economy-Transaktion darf weder nur das Budget noch nur das Inventar ändern. Ein Fehler in Presentation oder Animation darf dagegen den bestätigten Domain-State nicht zurückrollen.

## 16. Sicherheit und Datenintegrität

- IDs, Revisionen und Eventsequenzen sind technische Vertrauensanker.
- Eingaben werden an der zuständigen Schicht validiert.
- Unbekannte Journaltypen werden nicht persistiert oder replayt.
- Hashketten erkennen Manipulation, ersetzen aber keine Zugriffskontrolle.
- Netzwerkbestätigung ist für gemeinsame Transaktionen zukünftig autoritativ; der Transport ist noch nicht implementiert.
- Reale Ortsbezeichnungen erzeugen keine Zugangsberechtigung.

## 17. Testarchitektur

### 17.1 Runtime

`tests/runtime/` deckt unter anderem ab:

- Character Core,
- Action Resolver,
- Command Dispatcher,
- Persistence Kernel,
- Recovery und Fault Injection,
- Event State,
- Economy Vertical Slice,
- Character-Forge-Session.

### 17.2 Presentation

`tests/presentation/` prüft:

- Projektionen,
- Capabilities und Commands,
- Feedback,
- A4/A3-Verträge,
- Ranking/Network,
- HTML-Blueprint,
- vollständigen 0.7.2-Character-Forge-Slice.

### 17.3 Repository Health

`tools/repository_health.py` validiert Struktur und Informationskonsistenz. Es ersetzt keine fachlichen Runtime- oder Presentation-Tests.

### 17.4 Remote-Gates

Für einen PR nach `main` müssen auf exakt demselben Head erfolgreich sein:

- `runtime-core`,
- `presentation-core`,
- `repository-health`.

Lokale Prüfungen sind Vorbedingungen, aber kein Ersatz für fehlende Remote-Nachweise.

## 18. Erweiterungspunkte

### 18.1 Neue Action

1. fachlichen Zweck und Voraussetzungen definieren,
2. stabile Action-ID und Textschlüssel ergänzen,
3. Manifest und Schema einhalten,
4. Resolverwirkung und Ereignisse anbinden,
5. Action-Projektion ergänzen,
6. gezielten Vertrags- und Runtime-Test hinzufügen,
7. keine sichtbaren Texte in die Logik schreiben.

### 18.2 Neuer Journal-Ereignistyp

1. Ereignis fachlich begründen,
2. in `JOURNAL_MANIFEST.json` katalogisieren,
3. Payload-Form validieren,
4. Persistence und Replay anbinden,
5. Recovery-Verhalten testen,
6. Projection nur aus bestätigtem Ereignis ableiten.

### 18.3 Neue Eventphase

Eine neue Phase verändert den Fachvertrag und darf nicht nur in der UI ergänzt werden. Erforderlich sind mindestens Phasenmanifest, Domainübergänge, Gate-Regeln, Schemaabgleich, Replay und Regressionstests.

### 18.4 Neues Equipmentmerkmal

Das Merkmal gehört in den Katalog, wenn es eine Definition beschreibt, und ins Inventar, wenn es konkreten Besitz beschreibt. Preis- oder Verbrauchsregeln müssen deterministisch bleiben.

### 18.5 Neuer Client

Ein Client darf:

- Projektionen lesen,
- lokale View-Zustände halten,
- Application-Commands erzeugen und dispatchen,
- bestätigtes Feedback darstellen.

Ein Client darf nicht:

- Domainregeln nachimplementieren,
- State-Dateien direkt schreiben,
- Command-Erfolg vorwegnehmen,
- sichtbare Namen als IDs verwenden,
- unbestätigte Netzwerkdaten als autoritativ markieren.

## 19. Geplanter vollständiger Event-Loop

`0.8.3` soll die vorhandenen Kerne verbinden:

```text
EventState planen
→ Economy-Beschaffung und Reservierung
→ Transportvoraussetzungen prüfen
→ Aufbauaktionen ausführen
→ Soundcheck bestätigen
→ Livebetrieb und Krisen abwickeln
→ Abbau durchführen
→ Abrechnung buchen
→ Ruf-, Character- und Biografiefolgen erzeugen
→ A4/A3 projizieren
→ Save/Recovery des gesamten Ablaufs prüfen
```

Bis zu dieser Abnahme darf ein grafischer Client keinen zweiten, vorläufigen Event- oder Economy-Kern erhalten.

## 20. Nicht implementierte Bereiche

- vollständige Eventaktionen je Phase,
- Incident- und Krisenauflösung,
- Abrechnung mit vollständigen Ruf- und Character-Folgen,
- schreibender A4-Client,
- Clubsystem,
- Network-/Telegram-Transport,
- serverautoritatives gemeinsames Economy- und Eventspiel.

Diese Grenzen müssen in UI, Dokumentation und PR-Beschreibungen sichtbar bleiben.

## 21. Arbeitsablauf für externe Entwickler

1. `AGENTS.md` lesen.
2. `PROJEKTSTATUS.json` für den aktuellen Zustand lesen.
3. `TODO.md` für die kanonische nächste Arbeitseinheit lesen.
4. Architekturvertrag und direkten Fachvertrag öffnen.
5. zuständige Module, Manifeste, Schemas und Tests bestimmen.
6. Ziel, Abnahme, Scope, Grund, Risiken und Nicht-Ziele notieren.
7. kleinsten Patch an der kanonischen Zielstelle umsetzen.
8. nur relevante Prüfungen ausführen.
9. Diff gegen den Plan prüfen.
10. fachliche oder verbindliche Prozessänderungen im Changelog dokumentieren.
11. committen und PR mit erforderlichen Remote-Gates erstellen.
12. normalen PR ausschließlich über `/safe-merge` übernehmen lassen.

## 22. Definition of Done für Gameplay-Erweiterungen

Eine Gameplay-Erweiterung ist erst abgeschlossen, wenn:

- die fachliche Regel an genau einer kanonischen Stelle definiert ist,
- IDs, Payloads und Datenformen validiert sind,
- Domain keine UI- oder Dateisystemabhängigkeit erhält,
- dauerhafte Änderungen über katalogisierte Ereignisse laufen,
- Idempotenz und Revisionen berücksichtigt sind,
- Character-, Event- und Economy-Blöcke koexistieren,
- Replay und Recovery dasselbe Ergebnis erzeugen,
- Presentation nur bestätigte Daten zeigt,
- einfache Fehlermeldungen vorhanden sind,
- relevante lokale Tests grün sind,
- alle drei Remote-Gates auf demselben Head grün sind.

## 23. Kanonische Referenzen

| Thema | Referenz |
|---|---|
| Architektur | [`ARCHITEKTURVERTRAG.md`](ARCHITEKTURVERTRAG.md) |
| fachliche Landkarte | [`GAME_SCHEMA.md`](GAME_SCHEMA.md) |
| Character Forge | [`CHARACTER_FORGE.md`](CHARACTER_FORGE.md) |
| Progression | [`PROGRESSION_CONTRACT.md`](PROGRESSION_CONTRACT.md) |
| Gameplay Actions | [`GAMEPLAY_ACTION_CONTRACT.md`](GAMEPLAY_ACTION_CONTRACT.md) |
| Eventzustand | [`EVENT_STATE_0.8.1.md`](EVENT_STATE_0.8.1.md) |
| Economy | [`ECONOMY_0.8.2.md`](ECONOMY_0.8.2.md) |
| Persistenz | [`PERSISTENCE_CONTRACT.md`](PERSISTENCE_CONTRACT.md) |
| Recovery | [`RECOVERY_0.5.1.md`](RECOVERY_0.5.1.md) |
| Presentation | [`PRESENTATION_CONTRACT_0.6.md`](PRESENTATION_CONTRACT_0.6.md) |
| UI/UX | [`UI_UX_BLUEPRINT.md`](UI_UX_BLUEPRINT.md) |
| Repository-Navigation | [`REPOSITORY_INDEX.md`](REPOSITORY_INDEX.md) |
| einfacher Produktüberblick | [`SPIELBESCHREIBUNG_OHNE_TECHNIK.md`](SPIELBESCHREIBUNG_OHNE_TECHNIK.md) |
| aktueller Status | [`../PROJEKTSTATUS.json`](../PROJEKTSTATUS.json) |
| nächste Arbeit | [`../TODO.md`](../TODO.md) |

## 24. Technisches Glossar

| Begriff | Bedeutung |
|---|---|
| Domain | reine Spielregeln und fachliche Zustände |
| Application | koordiniert Commands und Anwendungsabläufe |
| Infrastructure | technische Speicherung, Recovery und externe Adapter |
| Presentation | schreibgeschützte Aufbereitung für Oberflächen |
| Command | ausdrückliche Absicht, Zustand zu verändern |
| Domain-Ereignis | bestätigte fachliche Tatsache |
| Projection | aus bestätigten Daten aufgebautes View-Modell |
| Idempotenz | Wiederholung erzeugt keine zweite Wirkung |
| Revision | monotone Versionsnummer eines Zustands |
| Append-only | vorhandene Einträge werden nie überschrieben |
| Kompensation | neues Ereignis gleicht ein altes aus |
| Atomarität | mehrere Änderungen erfolgen gemeinsam oder gar nicht |
| Replay | Zustand wird aus gespeicherten Ereignissen erneut aufgebaut |
| Recovery | kontrollierte Wiederherstellung nach Fehler oder Abbruch |
| Fail-closed | unsicherer Vorgang wird abgelehnt statt geraten |
| Vertical Slice | durchgängige Funktion über alle benötigten Schichten |
