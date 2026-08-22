<div align="center">

# BUNKERFREQUENZ

### Beton. Bass. Berlin.

**Techno-/FreeTekno-Crew-RPG · Character Forge · Event-Management · Living Districts · Property Progression**

<p>
  <img alt="Runtime Baseline 0.8.4 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.8.4--alpha.1-ff4d00">
  <img alt="Feature Stand 0.8.6 B validiert" src="https://img.shields.io/badge/Feature_Stand-0.8.6--B_validiert-7dff00">
  <img alt="Living Districts validiert" src="https://img.shields.io/badge/Living_Districts-validiert-00c2ff">
  <img alt="Property Purchase validiert" src="https://img.shields.io/badge/Property_Purchase-0.8.6--A_validiert-f2c744">
  <img alt="Property Upgrades validiert" src="https://img.shields.io/badge/Property_Upgrades-0.8.6--B_validiert-e840ff">
  <img alt="Hall of Tribute validiert" src="https://img.shields.io/badge/Hall_of_Tribute-validiert-ff7ad9">
  <img alt="Mergeweg Safe Merge" src="https://img.shields.io/badge/Mergeweg-%2Fsafe--merge-8a2be2">
</p>

> **Entdecken → planen → handeln → eskalieren → abrechnen → Stadt verändern → Orte übernehmen → ausbauen → aufsteigen.**

</div>

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

---

## ⚡ Projekt-Puls

| | Aktueller Stand |
|---|---|
| **Release-Baseline** | `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease |
| **Validierter Feature-Stand** | ✅ `0.8.6-B` |
| **Lokaler Game Client** | ✅ schreibender A4-Client, localhost-only |
| **Event-Loop** | ✅ Planung → Beschaffung → Aufbau → Live → Krise optional → Abbau → Settlement → completed |
| **Living World** | ✅ Street Encounters + persistente District-Metriken |
| **Ranking** | ✅ Competitive Top 10 + Hall of Tribute |
| **Immobilien** | ✅ 7 kaufbare Orte, bestätigtes Eigentum |
| **Ausbau** | ✅ 10 Ausbauarten, Level 1–3, atomare Kostenbuchung, Map-Wertwirkung |
| **Recovery** | ✅ Combined Replay für Character, Event, Economy, Incident, Settlement, District, Property und PropertyUpgrade |
| **Nächster Block** | `0.8.6-C – Berlin Ops Map PRO` |
| **Netzwerk/Telegram** | noch nicht implementiert; keine erfundenen Remote-Spieler |

> [!IMPORTANT]
> `0.8.6-B` ist **Feature-Fortschritt**, kein stiller Produktrelease. Die veröffentlichte Runtime-Baseline bleibt `0.8.4-alpha.1`, bis eine neue eigene Release-Abnahme durchgeführt wird.

---

## 🎮 In 60 Sekunden: Was ist das Spiel?

BUNKERFREQUENZ ist ein lokales Techno-/FreeTekno-Crew-RPG, in dem nicht eine starre Klasse, sondern bestätigtes Verhalten den Charakter und die Spielwelt formt.

```text
STRASSE / ENTDECKEN
      ↓
CHARAKTER & CREW ENTWICKELN
      ↓
EVENT PLANEN
      ↓
EQUIPMENT / CREW / ORT VORBEREITEN
      ↓
EVENT DURCHFÜHREN
      ↓
KRISE? → ENTSCHEIDUNG
      ↓
SETTLEMENT
      ↓
RUF · SKILLS · TRAITS · BIOGRAFIE
      ↓
DISTRICT-WERTE VERÄNDERN
      ↓
IMMOBILIEN ÜBERNEHMEN
      ↓
IMMOBILIEN AUSBAUEN
      ↓
HALL OF TRIBUTE / LANGZEITPROGRESSION
```

### Character Forge

- **16 Skills** statt fester Klassen
- **165 Trait-Namen** auf gemeinsamen, kontrollierbaren Effektfamilien
- Level 1–50, danach offene Resonanzränge
- Energie und Stress `0..100`
- Profilname, Alias, Spitznamen und Motto editierbar
- Biografie ausschließlich aus bestätigten Journal-Ereignissen

### Living World

- 8 stilisierte Berliner Bezirke
- 12 katalogisierte Spielorte
- `heat`, `prestige`, `police_pressure`, `scene_activity` persistent je Bezirk
- deterministische Street Encounters ohne Reload-Reroll
- Hall of Tribute mit bestätigtem Ranking

---

## 🏢 0.8.6 – Property Progression ✅

Mit 0.8.6 wird aus der bisher read-only vorbereiteten Immobilienbasis erstmals echte langfristige Progression.

### 0.8.6-A – Immobilien kaufen

Sieben City-Map-Orte besitzen einen kanonischen Kaufpreis. Der Client darf diesen Preis **nicht** mitsenden oder ändern.

```text
A4
 ↓ property.purchase(location_id)
GameClientSession
 ↓
PropertyService
 ↓
EconomyService – Geldautorität
 ↓
EIN atomarer Persistence-Commit
 ├─ economy.transaction_posted
 └─ world.property_purchased
 ↓
Economy + Event-Budget + PropertyState
```

Garantien:

- Kaufpreis ausschließlich aus `CITY_MAP_MANIFEST`
- bestätigter Character wird Eigentümer
- nicht kaufbare Orte fail-closed
- Doppelkäufe fail-closed
- kein Zwischenzustand „Geld weg, Eigentum fehlt“
- Property-Käufe sind nicht über den Equipment-Undo kompensierbar
- Combined Recovery rekonstruiert Geld und Eigentum gemeinsam
- dieselbe Ownership-Quelle markiert den Ort in der Berlin-Ops-Projection

**Remote-Abnahme:** PR #82 · Head `af582597fa2a899ab0cc0d062e128ec6b0e7dc1a` · Merge `192b3eb4ad9dc4272eafeddc8604f7265bdd30fa`.

### 0.8.6-B – Immobilien ausbauen

Eigentum bleibt rückwärtskompatibel im bestehenden `PropertyState`. Ausbau besitzt bewusst einen **separaten `PropertyUpgradeState`**.

```text
A4
 ↓ property.upgrade(location_id, upgrade_id)
GameClientSession
 ↓
PropertyUpgradeService
 ├─ prüft Eigentum + erlaubten Slot + aktuelles Level
 ├─ liest bestätigten ursprünglichen Kaufpreis
 └─ nutzt EconomyService für die Geldmutation
 ↓
EIN atomarer Commit
 ├─ economy.transaction_posted
 └─ world.property_upgraded
 ↓
Economy + Event-Budget + PropertyUpgradeState
```

#### Ausbauarten

| Ausbau | Primäre Wirkung pro Level |
|---|---|
| Schallschutz | Risiko ↓, Utility ↑ |
| Strom | Utility ↑, Risiko leicht ↓ |
| Fluchtwege | Risiko deutlich ↓ |
| Deko | Prestige + Audience Pull ↑ |
| Bühne | Prestige + Audience Pull + Utility ↑ |
| Bar | Audience Pull + Utility ↑, Risiko leicht ↑ |
| Lager | Utility ↑ |
| Security | Risiko ↓, Utility ↑ |
| Studio | Prestige + Underground + Utility ↑ |
| Office | Prestige + Utility ↑ |

#### Level- und Kostenvertrag

- maximales Ausbaulevel: **3**
- Level-Multiplikatoren: **1,00× / 1,50× / 2,25×**
- Basis ist der **bestätigte ursprüngliche Kaufpreis** des Ortes
- jede Ausbauart besitzt zusätzlich einen manifestdefinierten Kostenfaktor
- reine Ganzzahl-/Basispunktrechnung; kein Browser-Float und keine Rundungsdrift
- Ausbaukosten verändern den Equipment-Markt-Tick nicht
- Ausbaukäufe sind nicht kompensierbar

Der Browser sendet ausschließlich:

```text
property.upgrade
+ command_id
+ location_id
+ upgrade_id
```

Er darf **nicht** mitsenden:

- Preis
- Ziellevel
- Budgetdelta
- Wertdelta
- Menge
- Eigentümer

Diese Felder werden bei Manipulationsversuchen vor jedem Write abgewiesen.

#### Wirkung auf die Karte

Ausbau erzeugt keine zweite Bewertungsengine. Die bestätigten Ausbaulevel werden read-only in effektive Standortwerte übersetzt und anschließend an dieselbe bestehende `city_map_projection` übergeben.

```text
PropertyUpgradeState
      ↓
effektive Location-Werte 0..100
      ↓
city_map_projection
      ↓
kanonischer Score
      ↓
standard / strong / prime / legendary
```

**Remote-Abnahme 0.8.6-B:**

- PR #83
- Head `acbf6b1c5615137664ed4ad84fb0535bea297030`
- Runtime Core `32589287044` ✅
- Presentation Core `32589287132` ✅
- Repository Health `32589287056` ✅
- Release Acceptance `32589287152` ✅
- Release Package `32589287135` ✅
- Review-Threads: `0`
- `/safe-merge`: **PASS**
- Merge `0b301bc9004f60dbc3ce221a7c6b3e462766b5b7`

---

## 🗺️ Nächster Schritt: 0.8.6-C – Berlin Ops Map PRO

Jetzt ist der geeignete Zeitpunkt für den hochwertigen Kartenrenderer. Vorher wäre er nur eine hübsche Hülle um statische Daten gewesen. Jetzt existieren echte, bestätigte Quellen für:

- District-Metriken
- letzte District-Änderung
- 12 Locations
- Score und Tier
- Eigentum
- Ausbaulevel
- effektive Ausbauwerte
- Hall of Tribute

### Zielbild

**Retro-Autokarte × industrieller Berliner Control Room × taktische Aufbauspielkarte**.

Der Renderer bleibt strikt read-only:

```text
Domain / Application / Journal
            ↓
bestätigter State
            ↓
District / Property / Upgrade Projections
            ↓
City Map Projection
            ↓
BERLIN OPS MAP PRO
```

Die Karte darf hervorheben, filtern, fokussieren und erklären – aber weder Heat, Eigentum, Kosten noch Score selbst erfinden.

Aktiver Plan: [`TODO.md`](TODO.md)

---

## 🚀 Start für absolute Anfänger

### 1. Repository öffnen

Im Projektordner ein Terminal öffnen.

### 2. Spiel starten

```bash
./START_BUNKERFREQUENZ.sh
```

Für automatische freie Portwahl:

```bash
./START_BUNKERFREQUENZ.sh --port 0
```

Oder direkt:

```bash
python3 tools/start_a4_game_client.py
```

Der lokale Server bindet ausschließlich an `127.0.0.1`.

### 3. Was beim ersten Start passiert

Der First Run legt kontrolliert an:

1. GENESIS-Character
2. vorbereitetes Event
3. Economy-/Equipment-Katalog

Vorhandene Saves werden nicht still überschrieben.

### 4. Speichern

Jeder bestätigte Command wird unmittelbar journalisiert. Zusätzlich kann der A4-Client einen manuellen Snapshot/Checkpoint erzeugen.

---

## 🧱 Architektur

```text
DOMAIN
├─ CharacterState
├─ EventState
├─ EconomyState
├─ IncidentState
├─ SettlementState
├─ DistrictState
├─ PropertyState
└─ PropertyUpgradeState
        ↓
APPLICATION
├─ Character / Profile
├─ Street Encounter
├─ Event State / Execution
├─ Economy
├─ Incident
├─ Settlement
├─ District
├─ Property
└─ Property Upgrade
        ↓
PERSISTENCE
├─ append-only Journal
├─ Hashkette
├─ atomare State-Writes
├─ Snapshot
└─ Combined Recovery
        ↓
READ-ONLY PROJECTIONS
├─ Character / Feedback
├─ Ranking / Hall
├─ Living Districts
├─ Property / Upgrades
└─ Berlin Ops Map
        ↓
A4 GAME CLIENT / SPÄTER MAP PRO
```

### Harte Grenzen

| Ebene | Darf | Darf nicht |
|---|---|---|
| `domain` | Zustandsregeln und Invarianten | UI kennen |
| `application` | Use Cases und atomare Orchestrierung | Persistenz umgehen |
| `infrastructure` | Journal, State, Snapshot, Recovery | Gameplaytexte erfinden |
| `presentation` | bestätigte Daten darstellen | Domain-/Save-State direkt schreiben |
| `content` | Texte und katalogisierte Inhalte | technische Autorität ersetzen |

---

## 🛡️ Persistenz & Recovery

- append-only JSONL-Journal
- SHA-256-Hashkette
- atomare State-/Meta-Writes
- Snapshots
- Recovery aus gültigem State oder Snapshot + Journal-Replay
- Quarantäne beschädigter Journal-Tails
- Fault-Injection-Tests für durable Journalrecords vor State-Write

Combined Recovery kennt inzwischen:

```text
Character
→ Event
→ Economy
→ Incident
→ Settlement
→ District
→ Property
→ PropertyUpgrade
```

Ein besonders wichtiger Vertrag für 0.8.6 lautet:

> **Geld und Eigentum/Ausbau dürfen nach einem Crash niemals auf unterschiedlichen bestätigten Ständen verbleiben.**

---

## 🏙️ Berlin Ops Datenbasis

- **8 Bezirke:** Mitte, Friedrichshain, Kreuzberg, Neukölln, Wedding, Lichtenberg, Treptow, Charlottenburg
- **12 Locations**
- **7 kaufbare Properties**
- **10 Upgrade-Arten**
- exakt **1 Hall of Tribute**

Die Karte ist eine **stilisierte Spielkarte**, keine reale Navigation. Sie verwendet 0–100-Spielkoordinaten und benötigt kein Geocoding.

Location-Werte:

- `prestige`
- `audience_pull`
- `risk`
- `underground_factor`
- `utility`

District-Werte:

- `heat`
- `prestige`
- `police_pressure`
- `scene_activity`

---

## 🏆 Hall of Tribute

Die Hall verwendet dieselbe kanonische Ranking-Engine wie die übrige Presentation.

Aktuell lokal verfügbar:

- Ruf
- Level
- Resonanz
- eindeutige Top-10-Plätze
- Aufstieg `↑`
- Abstieg `↓`
- gehalten `→`
- neu `★`

Ohne bestätigte Netzwerkdaten werden keine Gegner konstruiert.

Später vorbereitet: saisonale Titel wie **Lärmadel, Bunkerbaron, Kabelkönig, Pegelpapst, Stromheiland, Betonlegende und Nachtminister**.

---

## ✅ Wichtige validierte Meilensteine

| Iteration | Kern | Merge |
|---|---|---|
| 0.8.3-C | Settlement / vollständiger Eventabschluss | `5ae811333878...` |
| 0.8.4 | schreibender A4 Game Client | `28459c197489...` |
| 0.8.4-alpha.1 | erster freigegebener lokaler Release | `3fdb5cc3d57e...` |
| 0.8.5-A | Competitive Ranking | `b41d8f416679...` |
| 0.8.5-B | Profilpersonalisierung | `5a9eed536d48...` |
| 0.8.5-C | Street Encounters | `38de9f42c290...` |
| 0.8.5-D | Living Districts | `98c8b84715cc...` |
| 0.8.5-E | Hall of Tribute | `d383a3f364c6...` |
| **0.8.6-A** | **Property Purchase** | `192b3eb4ad9d...` |
| **0.8.6-B** | **Property Upgrades** | `0b301bc9004f...` |

---

## 📦 Release-Baseline

Aktueller bewusst freigegebener Release:

```text
BUNKERFREQUENZ-0.8.4-alpha.1.zip
SHA-256:
fccf16ee3728827ba4eba0dfd0e3cbaf844dd68c382b3c29c766f94a7ef85146
```

Das Release-Paket wird reproduzierbar gebaut und aus einem frisch entpackten Zielordner smoke-getestet.

0.8.5 und 0.8.6 sind danach validierte Feature-Entwicklung auf `main`. Eine neue Produktversion wird erst nach einer eigenen Release-Iteration festgelegt.

---

## 🧪 Qualitäts-Gates

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
PYTHONPATH=src:. python3 -m unittest discover -s tests/repository -v
PYTHONPATH=src python3 tools/repository_health.py
```

Normale PRs werden erst übernommen, wenn der exakte Head aktuell zu `main` ist, die Required Checks grün sind und keine ungelösten Review-Threads verbleiben.

```text
PR
 ↓
Runtime Core ✅
Presentation Core ✅
Repository Health ✅
 ↓
Release Acceptance / Package bei Featurepfaden ✅
 ↓
0 Review-Threads
 ↓
aktueller main enthalten
 ↓
/safe-merge
 ↓
Main-Provenienz
 ↓
SAFE MERGE PASS
```

---

## 🗂️ Schnellzugriff

| Gesucht | Datei |
|---|---|
| aktueller Maschinenstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| aktive Arbeit | [`TODO.md`](TODO.md) |
| Ausbauvorrat | [`FEATURE_POOL.md`](FEATURE_POOL.md) |
| Projektmanifest | [`PROJEKTMANIFEST.json`](PROJEKTMANIFEST.json) |
| A4 First Run | [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md) |
| Event State | [`docs/EVENT_STATE_0.8.1.md`](docs/EVENT_STATE_0.8.1.md) |
| Event Actions | [`manifests/EVENT_ACTION_MANIFEST.json`](manifests/EVENT_ACTION_MANIFEST.json) |
| Incident | [`manifests/INCIDENT_MANIFEST.json`](manifests/INCIDENT_MANIFEST.json) |
| Settlement | [`manifests/SETTLEMENT_MANIFEST.json`](manifests/SETTLEMENT_MANIFEST.json) |
| City Map | [`manifests/CITY_MAP_MANIFEST.json`](manifests/CITY_MAP_MANIFEST.json) |
| Living Districts | [`manifests/DISTRICT_STATE_MANIFEST.json`](manifests/DISTRICT_STATE_MANIFEST.json) |
| Property | [`manifests/PROPERTY_MANIFEST.json`](manifests/PROPERTY_MANIFEST.json) |
| Property Upgrades | [`manifests/PROPERTY_UPGRADE_MANIFEST.json`](manifests/PROPERTY_UPGRADE_MANIFEST.json) |
| Hall of Tribute | [`manifests/HALL_OF_TRIBUTE_MANIFEST.json`](manifests/HALL_OF_TRIBUTE_MANIFEST.json) |
| Ranking | [`manifests/RANKING_NETWORK_MANIFEST.json`](manifests/RANKING_NETWORK_MANIFEST.json) |
| Persistence | [`docs/PERSISTENCE_CONTRACT.md`](docs/PERSISTENCE_CONTRACT.md) |
| Recovery | [`docs/RECOVERY_0.5.1.md`](docs/RECOVERY_0.5.1.md) |
| Safe Merge | [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md) |
| Entwicklerhandbuch | [`docs/ENTWICKLERHANDBUCH.md`](docs/ENTWICKLERHANDBUCH.md) |
| Änderungshistorie | [`CHANGELOG.md`](CHANGELOG.md) |

---

## 🔧 Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Keine zweite Architektur, keine UI-Fachlogik und keine stillen Versionssprünge.

Normale PRs nach `main` werden ausschließlich über `/safe-merge` übernommen.

Details: [`AGENTS.md`](AGENTS.md) · [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) · [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md)
