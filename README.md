<div align="center">

# BUNKERFREQUENZ

### Beton. Bass. Berlin.

**Techno-/FreeTekno-Crew-RPG · Character Forge · Event-Management · Bunker-Entwicklung**

<p>
  <img alt="Runtime Baseline 0.8.4 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.8.4--alpha.1-ff4d00">
  <img alt="Character Forge 0.7.2 validiert" src="https://img.shields.io/badge/Character_Forge-0.7.2_validiert-7dff00">
  <img alt="Economy 0.8.2 remote validiert" src="https://img.shields.io/badge/Economy-0.8.2_remote_validiert-f2c744">
  <img alt="Event Actions 0.8.3 A validiert" src="https://img.shields.io/badge/Event_Actions-0.8.3--A_validiert-00c2ff">
  <img alt="Crisis und Berlin Map 0.8.3 B validiert" src="https://img.shields.io/badge/Crisis_Map-0.8.3--B_validiert-e840ff">
  <img alt="Settlement 0.8.3 C remote validiert" src="https://img.shields.io/badge/Settlement-0.8.3--C_remote_validiert-2ee6a6">
  <img alt="A4 Game Client 0.8.4 remote validiert" src="https://img.shields.io/badge/A4_Game_Client-0.8.4_remote_validiert-ff7ad9">
  <img alt="First Playable Alpha 0.8.4 alpha 1" src="https://img.shields.io/badge/First_Playable_Alpha-0.8.4--alpha.1-7dff00">
  <img alt="Mergeweg Safe Merge" src="https://img.shields.io/badge/Mergeweg-%2Fsafe--merge-8a2be2">
</p>

> **Entdecken → planen → handeln → eskalieren → entscheiden → abrechnen → entwickeln.**  
> Verhalten, Training, Entscheidungen und Krisen formen die Crew – ohne starre Startklassen.

</div>

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

---

## ⚡ Projekt-Puls

| | Aktueller Stand |
|---|---|
| **Runtime-Baseline** | `0.8.4-alpha.1` |
| **Erstes lokal spielbares Alpha** | ✅ remote validiert, reproduzierbar paketiert und per `/safe-merge` übernommen |
| **Release PR #73** | Head `ece6c145bb07...` · Runtime `32576855723` · Presentation `32576855749` · Repository Health `32576855738` · Release Acceptance `32576855720` · Release Package `32576855768` · `SAFE MERGE PASS` · Merge `3fdb5cc3d57e...` |
| **Release-Artefakt** | `BUNKERFREQUENZ-0.8.4-alpha.1.zip` · SHA-256 `fccf16ee3728827ba4eba0dfd0e3cbaf844dd68c382b3c29c766f94a7ef85146` |
| **Release-Abnahme** | PR #72 · frischer Checkout, Launcher, Fehlerpfade, Save/Restart/Recovery · `SAFE MERGE PASS` |
| **0.8.4** | lokaler schreibender A4-Client, First Run, kompletter Event-Smoke, Save/Restart/Recovery |
| **Nächster Entwicklungsblock** | **0.8.5 – persistente Bezirksdynamik** aus bestätigten Settlement-/Event-Ergebnissen |
| **Persistenz** | append-only Journal, Autosave, Snapshot, Recovery, kompensierender Undo; fehlender State bei gültigem Head-Snapshot regressionsgehärtet |
| **Repository-Sicherheit** | `/safe-merge` + Main Integrity; native Branch Protection bleibt zusätzliche Härtung |
| **Berlin Ops Map** | getestete read-only Foundation; persistenter District-State und hochwertiger Renderer folgen nach dem Alpha |
| **Telegram / Sync** | geplant; Transport-/Serverphase noch nicht implementiert |

> [!IMPORTANT]
> `0.8.4-alpha.1` ist die erste **freigegebene lokal spielbare Runtime-Baseline**. Produktversion, Release-Abnahme und reproduzierbares Paket sind getrennt nachgewiesen. Der nächste Entwicklungsblock darf diese Baseline nicht still umbenennen; eine neue Produktversion entsteht erst nach einer neuen eigenen Abnahme.

---

## ✅ Release 0.8.4-alpha.1

Der vollständige lokale Kernpfad ist jetzt als Release bestätigt:

```text
First Run
→ Planung
→ Beschaffung
→ Equipment kaufen/reservieren
→ Transport
→ Aufbau
→ Soundcheck
→ Live
→ optionale Krise
→ Abbau
→ Settlement
→ completed
→ Checkpoint
→ Neustart / Recovery
```

Der Release-Prozess prüft zusätzlich:

- echten Launcherprozess aus frischem Checkout
- localhost HTTP-Health
- freie Portwahl mit `--port 0`
- verständliche Fehler für belegten Port, fehlende Dateien und unbrauchbaren Save-Pfad
- zwei **byte-identische** Builds desselben ZIPs
- SHA-256-Sidecar
- entpacktes Paket aus frischem Zielordner
- Klickstart über `START_BUNKERFREQUENZ.sh`
- First Run aus dem entpackten Paket bis `completed`
- Checkpoint nach abgeschlossenem Event

Maschinenlesbarer Release-Nachweis: [`reports/RELEASE_0.8.4-alpha.1.json`](reports/RELEASE_0.8.4-alpha.1.json)

**Nicht Bestandteil dieses Alpha-Releases:** Telegram-/Netzwerk-Sync, öffentlicher Serverbetrieb, persistente Bezirksdynamik, Immobilienkauf/-ausbau, saisonale Hall-of-Tribute-Wertungen und ein hochwertiger Kartenrenderer.

---

## 🎛️ Der Kern des Spiels

```text
ENTDECKEN
   ↓
PLANEN
   ↓
BESCHAFFEN / TRAINIEREN / VERNETZEN
   ↓
AUFBAUEN / BOOKEN / SOUND CHECKEN
   ↓
EVENT
   ↓
OPTIONALE KRISE / ENTSCHEIDUNG
   ↓
ABBAU / ABRECHNUNG
   ↓
SKILLS · TRAITS · BIOGRAFIE · LEVEL · RESONANZ · RUF
   ↓
NEUE ORTE / IMMOBILIEN / MÖGLICHKEITEN
```

### Was Charaktere wirklich verändert

- **16 Skills** statt fester Klassen
- **165 individuelle Trait-Namen** über 15 gemeinsame Effektfamilien
- Training, Praxis, Krisen, Teamplay, Erkundung, Erfolg und Scheitern erzeugen unterschiedliche Evidenz
- Spezialisierungen entstehen aus dauerhaftem Verhalten – nicht aus einer Klassenwahl
- Level 1–50 gehen anschließend in **offene Resonanzränge** über
- dynamische Biografie entsteht ausschließlich aus bestätigten Journal-Ereignissen

---

## 🧱 Was bereits funktioniert

<table>
<tr>
<td valign="top" width="33%">

### Character Core

- 11 Hauptfiguren mit gleicher Startbasis
- editierbare Namen, Alias, Spitznamen, Motto
- deterministische Action Resolution
- Skills, Traits, Spezialisierung
- Level + Open-End-Resonanz
- Energie und Stress `0–100`

</td>
<td valign="top" width="33%">

### Persistence Core

- append-only Journal
- SHA-256-Hashkette
- atomare State-Writes
- Autosave
- Snapshots + Replay
- Recovery Receipt
- Quarantäne beschädigter Tails
- kompensierender Profil-Undo
- Snapshot-basierte Wiederherstellung eines fehlenden State-Checkpoints

</td>
<td valign="top" width="33%">

### Event / Client / World

- Event State + Economy
- 8 kanonische Event-Aktionen
- Crisis-/Incident-State
- 6 Krisentypen mit Reaktionswegen
- Settlement-State + atomarer Eventabschluss
- **schreibender lokaler A4-Game-Client**
- First Run + Save/Restart/Recovery-Smoke
- reproduzierbares lokales Alpha-Paket
- Berlin Ops Map Foundation
- Hall of Tribute
- Immobilien-/Upgrade-Datenbasis

</td>
</tr>
</table>

---

## 🏗️ Event-, Crisis- und Settlement-Vertrag

Der bestätigte Fachpfad bleibt die einzige Autorität:

```text
draft → planning → procurement → transport → setup → soundcheck → live ↔ crisis → teardown → settlement → completed
```

- Event-Aktionen laufen über `EventExecutionService`.
- Equipment/Budget laufen über `EconomyService`.
- Krisen laufen über `IncidentService`.
- `completed` wird ausschließlich durch `SettlementService` erzeugt.
- Der Browser dupliziert keine dieser Regeln.
- Persistierte Zustände und Journal-Ereignisse bleiben die Autorität für Save/Restart/Recovery.

Details: [`docs/EVENT_STATE_0.8.1.md`](docs/EVENT_STATE_0.8.1.md) · [`docs/CRISIS_CITY_0.8.3-B.md`](docs/CRISIS_CITY_0.8.3-B.md) · [`docs/SETTLEMENT_0.8.3-C.md`](docs/SETTLEMENT_0.8.3-C.md)

---

## 🗺️ Berlin Ops Map Foundation

Die Weltkarte ist ausdrücklich **stilisierte Spielkarte, keine Navigation**.

Aktuelle Datenbasis:

- 8 Bezirke
- 12 Spielorte
- 7 kaufbare Objekte
- 10 Ausbauarten
- 1 Hall of Tribute
- vorbereitete District-Metriken: `heat`, `prestige`, `police_pressure`, `scene_activity`

Diese District-Metriken sind in `0.8.4-alpha.1` noch **nicht persistent**. Genau das ist der nächste sinnvolle Gameplay-Schritt: bestätigte Settlement-Ergebnisse sollen künftig nachvollziehbar den Bezirkszustand verändern.

Vertrag: [`manifests/CITY_MAP_MANIFEST.json`](manifests/CITY_MAP_MANIFEST.json)

---

## 🎮 Schreibender A4-Game-Client

```text
A4 Browser
  ↓ JSON-Command
GameClientSession
  ↓
EventExecutionService / EconomyService / IncidentService / SettlementService
  ↓
PersistenceKernel
  ↓
Bestätigter State
  ↓
read-only a4_game_projection
  ↓
A4 Browser
```

Wesentliche Garantien:

- Command-Allowlist und strikte erlaubte Felder
- Eventbuttons/Blocker direkt aus Runtime-Availability
- Browser übersetzt Blocker nur in verständliche Texte
- lokaler Server bindet nur an `127.0.0.1`
- statische Auslieferung nur aus `web/a4/`
- First Run nur auf leerem GENESIS-Stand
- vorhandene Saves werden nicht überschrieben
- Snapshot/Checkpoint, Neustart und Recovery verwenden denselben bestätigten Zustand

Start-/Spielanleitung: [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md)

---

## 🧭 Einstieg ohne Vorwissen

1. Spielidee: [`docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md`](docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md)
2. **A4-First-Run Schritt für Schritt:** [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md)
3. Spieler-Einstieg: [`docs/SPIELERANLEITUNG.md`](docs/SPIELERANLEITUNG.md)
4. Entwicklergesamtbild: [`docs/SPIELBESCHREIBUNG_TECHNISCH.md`](docs/SPIELBESCHREIBUNG_TECHNISCH.md)
5. nächster Entwicklungsblock: [`TODO.md`](TODO.md)

### Spiel starten

```bash
./START_BUNKERFREQUENZ.sh
```

Alternativ:

```bash
python3 tools/start_a4_game_client.py
```

Automatisch freien Port wählen:

```bash
./START_BUNKERFREQUENZ.sh --port 0
```

---

## 🗂️ Schnellzugriff

| Ich suche … | Dann hier entlang |
|---|---|
| Release-Nachweis | [`reports/RELEASE_0.8.4-alpha.1.json`](reports/RELEASE_0.8.4-alpha.1.json) |
| vollständige Spielidee ohne Technik | [`docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md`](docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md) |
| technische Gesamtbeschreibung | [`docs/SPIELBESCHREIBUNG_TECHNISCH.md`](docs/SPIELBESCHREIBUNG_TECHNISCH.md) |
| A4 First Run | [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md) |
| A4 Schreibgrenze | [`docs/A4_WRITING_CLIENT_0.8.4.md`](docs/A4_WRITING_CLIENT_0.8.4.md) |
| aktueller Entwicklungsstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| nächste Aufgaben | [`TODO.md`](TODO.md) |
| Event Actions | [`manifests/EVENT_ACTION_MANIFEST.json`](manifests/EVENT_ACTION_MANIFEST.json) |
| Crisis + Berlin Map | [`docs/CRISIS_CITY_0.8.3-B.md`](docs/CRISIS_CITY_0.8.3-B.md) |
| Settlement | [`docs/SETTLEMENT_0.8.3-C.md`](docs/SETTLEMENT_0.8.3-C.md) |
| Release Manifest | [`manifests/RELEASE_MANIFEST.json`](manifests/RELEASE_MANIFEST.json) |
| Repository Guard | [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) |
| `/safe-merge` | [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md) |
| Änderungshistorie | [`CHANGELOG.md`](CHANGELOG.md) |

---

## 🧩 Architektur in 30 Sekunden

```text
Domain: CharacterState + EventState + EconomyState + IncidentState + SettlementState
  ↓
Application: Character / Event / Economy / Execution / Incident / Settlement Services
  ↑                     ↓
  └──── GameClientSession (nur Routing/Orchestrierung, keine zweite Fachlogik)
                        ↓
Persistence: Journal + State + Snapshot + Recovery
                        ↓
Read-only Projections
  ├─→ Character / Feedback
  ├─→ Ranking
  ├─→ Berlin Ops Map
  └─→ A4 Game Projection
                        ↓
A4 Game Client / A3 / spätere Kartenansicht
```

---

## 🛡️ Repository-Sicherheit

```text
Pull Request
   ↓
aktueller main enthalten?
   ↓
Runtime Core ✅
Presentation Core ✅
Repository Health ✅
   ↓
0 offene Review-Threads
   ↓
/safe-merge
   ↓
Merge exakt 1×
   ↓
Main-Provenienz
   ↓
SAFE MERGE PASS
```

Release-PRs prüfen zusätzlich `Release Acceptance` und `Release Package`, wenn diese Workflows Bestandteil des Releases sind.

---

## 🧪 Gezielte Prüfungen

### Runtime Core

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
```

### Presentation Core

```bash
PYTHONPATH=src python3 -m compileall -q src/bunkerfrequenz/presentation
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

### Repository Health

```bash
PYTHONPATH=src python3 -m compileall -q src tools/repository_health.py tools/github_merge_guard.py tools/github_merge_guard_retry.py tests/repository
PYTHONPATH=src:. python3 -m unittest discover -s tests/repository -v
PYTHONPATH=src python3 tools/repository_health.py
```

### Release Package

```bash
PYTHONPATH=src:. python3 -m unittest tests.runtime.test_release_package -v
python3 tools/build_release.py --output-dir dist
```

---

## 📚 Verbindliche Verträge

- [`docs/CHARACTER_FORGE.md`](docs/CHARACTER_FORGE.md)
- [`docs/PROGRESSION_CONTRACT.md`](docs/PROGRESSION_CONTRACT.md)
- [`docs/GAMEPLAY_ACTION_CONTRACT.md`](docs/GAMEPLAY_ACTION_CONTRACT.md)
- [`docs/EVENT_STATE_0.8.1.md`](docs/EVENT_STATE_0.8.1.md)
- [`manifests/EVENT_ACTION_MANIFEST.json`](manifests/EVENT_ACTION_MANIFEST.json)
- [`docs/CRISIS_CITY_0.8.3-B.md`](docs/CRISIS_CITY_0.8.3-B.md)
- [`manifests/INCIDENT_MANIFEST.json`](manifests/INCIDENT_MANIFEST.json)
- [`docs/SETTLEMENT_0.8.3-C.md`](docs/SETTLEMENT_0.8.3-C.md)
- [`manifests/SETTLEMENT_MANIFEST.json`](manifests/SETTLEMENT_MANIFEST.json)
- [`docs/A4_WRITING_CLIENT_0.8.4.md`](docs/A4_WRITING_CLIENT_0.8.4.md)
- [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md)
- [`reports/A4_CLIENT_VALIDATION_0.8.4.json`](reports/A4_CLIENT_VALIDATION_0.8.4.json)
- [`reports/RELEASE_ACCEPTANCE_ALPHA.json`](reports/RELEASE_ACCEPTANCE_ALPHA.json)
- [`reports/RELEASE_0.8.4-alpha.1.json`](reports/RELEASE_0.8.4-alpha.1.json)
- [`manifests/CITY_MAP_MANIFEST.json`](manifests/CITY_MAP_MANIFEST.json)
- [`docs/PERSISTENCE_CONTRACT.md`](docs/PERSISTENCE_CONTRACT.md)
- [`docs/RECOVERY_0.5.1.md`](docs/RECOVERY_0.5.1.md)
- [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md)
- [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md)

---

## 🔧 Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Normale PRs nach `main` werden ausschließlich über `/safe-merge` übernommen. Dafür müssen `runtime-core`, `presentation-core` und `repository-health` auf dem exakten PR-Head grün sein; der Branch muss den aktuellen `main` enthalten und alle Review-Threads müssen gelöst sein.

Details: [`AGENTS.md`](AGENTS.md) · [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) · [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md)