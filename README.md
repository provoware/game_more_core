<div align="center">

# BUNKERFREQUENZ

### Beton. Bass. Berlin.

**Techno-/FreeTekno-Crew-RPG · Character Forge · Event-Management · Bunker-Entwicklung**

<p>
  <img alt="Runtime Baseline 0.5.2 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.5.2--alpha.1-ff4d00">
  <img alt="Character Forge 0.7.2 validiert" src="https://img.shields.io/badge/Character_Forge-0.7.2_validiert-7dff00">
  <img alt="Economy 0.8.2 remote validiert" src="https://img.shields.io/badge/Economy-0.8.2_remote_validiert-f2c744">
  <img alt="Event Actions 0.8.3 A validiert" src="https://img.shields.io/badge/Event_Actions-0.8.3--A_validiert-00c2ff">
  <img alt="Crisis und Berlin Map 0.8.3 B validiert" src="https://img.shields.io/badge/Crisis_Map-0.8.3--B_validiert-e840ff">
  <img alt="Mergeweg Safe Merge" src="https://img.shields.io/badge/Mergeweg-%2Fsafe--merge-8a2be2">
</p>

> **Entdecken → planen → handeln → eskalieren → entscheiden → auswerten → entwickeln.**  
> Verhalten, Training, Entscheidungen und Krisen formen die Crew – ohne starre Startklassen.

</div>

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

---

## ⚡ Projekt-Puls

| | Aktueller Stand |
|---|---|
| **Runtime-Baseline** | `0.5.2-alpha.1` |
| **Letzte remote validierte Feature-Stufe** | `0.8.3-B – Crisis Engine + Berlin Ops Map Foundation` |
| **0.8.3-B-Abnahme** | PR #63 · Head `4a83cecc7298...` · Runtime Core `32559629560`, Presentation Core `32559629773`, Repository Health `32559629667` grün · 6 Review-Threads gelöst · `SAFE MERGE PASS` · Merge `816a3f1dd83d...` |
| **Nächster Pflichtblock** | `0.8.3-C – Settlement & Consequences` |
| **0.8.3-B1** | 6 Incident-Typen × 3 Reaktionen, atomarer Crisis-Lifecycle, pending Settlement, Recovery |
| **0.8.3-B2** | 8 Bezirke, 12 Orte, 7 kaufbare Objekte, Hall of Tribute, Score-/Tier-Projektion |
| **Weg zum ersten spielbaren Release** | `0.8.3-C Settlement/Folgen → vollständigen Loop abnehmen → schreibender A4-Client` |
| **Character Forge** | A4 Ops Deck + A3 Cinematic Forge auf derselben bestätigten Fachbasis |
| **Persistenz** | append-only Journal, 60-Sekunden-Autosave, Snapshot, Recovery, kompensierender Undo |
| **Repository-Sicherheit** | `/safe-merge` + Main Integrity; native Branch Protection bleibt zusätzliche Härtung |
| **Grafischer Renderer** | statischer HTML-Blueprint vorhanden; Berlin Ops Map derzeit als getestete read-only Projection, noch kein schreibender Kartenclient |
| **Telegram / Sync** | geplant; Transport-/Serverphase noch nicht implementiert |

> [!IMPORTANT]
> `VERSION.json` bezeichnet die letzte **versionierte Runtime-Baseline**. Feature-Meilensteine können weiter sein und werden getrennt in `PROJEKTSTATUS.json` und `TODO.md` geführt.

---

## 🚦 Was bis zum Release noch fehlt

Der aktuelle Stand ist eine validierte Spiellogik mit schreibgeschützter Präsentationsbasis – noch kein auslieferbarer Game-Client. Für das erste **spielbare Alpha-Release** bleiben zwei Pflichtblöcke:

1. **0.8.3-C Settlement & Consequences:** bestätigte Krisenfolgen über die vorhandenen Economy-/Character-Verträge buchen, Ruf/Stress/Stabilität/Heat anwenden, `event.completed` erzeugen und den Gesamtpfad inklusive Recovery testen.
2. **Release-Kandidat:** danach A4 als kleinsten schreibenden Client anbinden, Ersteinstieg und Save/Recovery-Smoke-Test nachweisen und erst dann Version/Release-Artefakt festlegen.

**Nicht blockierend für das erste lokale Alpha:** Telegram-/Netzwerk-Sync, öffentlicher Serverbetrieb, persistente Bezirksdynamik, Immobilienausbau, Hall-of-Tribute-Saisons und native GitHub-Branch-Protection.

Die genaue Reihenfolge steht in [`TODO.md`](TODO.md#p0--pflichtpfad-zum-ersten-spielbaren-alpha).

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
KRISE / ENTSCHEIDUNG
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
- 60-Sekunden-Autosave
- Snapshots + Replay
- Recovery Receipt
- Quarantäne beschädigter Tails
- kompensierender Profil-Undo

</td>
<td valign="top" width="33%">

### Event / World

- Event State + Economy
- 8 kanonische Event-Aktionen
- Crisis-/Incident-State
- 6 Krisentypen mit Reaktionswegen
- Berlin Ops Map Foundation
- Hall of Tribute
- Immobilien-/Upgrade-Datenbasis

</td>
</tr>
</table>

---

## 🏗️ 0.8.1 – Event State Foundation

0.8.1 setzt neben den Character-Zustand einen eigenen, journalfähigen `event`-Block. Character- und Eventdaten ersetzen sich beim Speichern nicht gegenseitig; Recovery kann beide Blöcke gemeinsam aus dem Journal rekonstruieren.

| Eventbereich | Vertrag |
|---|---|
| **Ort** | technische ID, Anzeigename, Region und Zugangsstatus |
| **Budget** | Änderungen laufen seit 0.8.2 über bestätigte Economy-Transaktionen |
| **Acts** | geplant / bestätigt / abgesagt |
| **Crew** | Character-ID, Rolle und Verfügbarkeit |
| **Equipment** | Anforderung und Readiness aus bestätigtem Besitz/Reservierung |
| **Zeitfenster** | ISO-8601 mit UTC-Offset und Zeitzone |
| **Sicherheit** | `unreviewed`, `cleared`, `restricted`, `blocked` |
| **Revision** | monotone Revision; veraltete Schreibversuche werden abgewiesen |

```text
draft → planning → procurement → transport → setup → soundcheck → live ↔ crisis → teardown → settlement → completed
```

> [!CAUTION]
> Ab `transport` verlangt der Domain-Vertrag einen gesetzten Ort, verifizierten Zugangsstatus, ein gültiges Zeitfenster und `safety_status=cleared`. Aus einem real klingenden Ortsnamen wird niemals automatisch eine Berechtigung abgeleitet.

Details: [`docs/EVENT_STATE_0.8.1.md`](docs/EVENT_STATE_0.8.1.md)

---

## ⚙️ 0.8.3-A – Event Execution Engine ✅

Die Phasenmaschine ist nicht mehr nur ein frei adressierbarer technischer Übergang. `EventExecutionService` stellt einen verbindlichen Aktionspfad bereit und liefert dieselben Blocker, die beim Execute tatsächlich geprüft werden.

```text
begin_planning
→ begin_procurement
→ start_transport
→ begin_setup
→ confirm_soundcheck
→ start_live
→ finish_live
→ finish_teardown
→ settlement
```

Wesentliche Regeln:

- bestätigte Acts/Crew und positives Budget vor der Beschaffung
- vollständige Crew-/Act-Bestätigung und Equipment-Readiness vor Transport/Live
- Ort, Zugang, Zeitfenster und Sicherheitsfreigabe für physische Phasen
- append-only Journal über `event.phase_changed`
- persistierter Eventzustand ist alleinige Autorität
- idempotente Wiederholung desselben Commands
- kein `completed`, bevor 0.8.3-C Settlement definiert

Maschinenlesbarer Vertrag: [`manifests/EVENT_ACTION_MANIFEST.json`](manifests/EVENT_ACTION_MANIFEST.json)

---

## 🚨 0.8.3-B1 – Crisis / Incident Engine ✅

Ein laufendes Event kann jetzt tatsächlich eskalieren. Die Krise ist kein UI-Effekt, sondern eigener persistierter Zustand.

```text
live
 ↓ Incident öffnen – atomarer Commit
crisis + IncidentState.active
 ↓ Response auswählen
crisis
 ↓ atomarer Resolve-Commit
live | teardown | cancelled
```

### Startkatalog

- Stromausfall
- Security-Probleme
- Equipment-Ausfall
- verspäteter Act
- Crowd Overload
- Lärmdruck

Jeder Typ besitzt drei katalogisierte Reaktionen. Severity `1–5` skaliert die Einzeleffekte deterministisch; mehrere bestätigte Krisen dürfen kumulierte Settlement-Summen über einzelne Effektgrenzen hinaus bilden.

### Warum Folgen zunächst nur vorgemerkt werden

Krisen erzeugen bestätigte Folgen auf Budget, Ruf, Crew-Stress, Stabilität und Heat. Diese stehen im `IncidentState.pending_settlement`, werden aber **noch nicht direkt** auf Economy oder Character geschrieben. Damit bleibt die 0.8.2-Regel erhalten: Geld ändert sich nur über bestätigte Economy-Transaktionen. Die eigentliche Buchung folgt in 0.8.3-C.

Der Replay prüft den Event-Kontext erneut; ein offener Incident darf nur mit seinem gespeicherten Vertragsstand aufgelöst werden.

Vertrag: [`docs/CRISIS_CITY_0.8.3-B.md`](docs/CRISIS_CITY_0.8.3-B.md) · [`manifests/INCIDENT_MANIFEST.json`](manifests/INCIDENT_MANIFEST.json)

---

## 🗺️ 0.8.3-B2 – Berlin Ops Map Foundation ✅

Die Welt bekommt eine eigene Handlungsebene. Sie ist ausdrücklich **stilisierte Spielkarte, keine Navigation**: 0–100-Koordinaten statt realer Adresslogik machen sie offline, portabel und rendererunabhängig.

### Stilrichtung

**Retro-Autokarte × moderner Control Room**

- entsättigte Kartengrundfläche
- transparente Bezirkszonen
- kontrastreiche Neonmarker
- Wert-/Tier-Hervorhebung statt beliebiger Dekoration
- Halo, Pulse und Ranking-Badge für Premium-Orte
- Reduced-Motion-Fallback ohne Informationsverlust

### Aktuelle Datenbasis

- **8 Bezirke:** Mitte, Friedrichshain, Kreuzberg, Neukölln, Wedding, Lichtenberg, Treptow, Charlottenburg
- **12 Spielorte**
- **7 kaufbare Objekte**
- **10 Ausbauarten**
- exakt **1 Hall of Tribute**

Jeder Ort besitzt `prestige`, `audience_pull`, `risk`, `underground_factor` und `utility`. Daraus berechnet die read-only Projection einen deterministischen Score und die Tiers `standard / strong / prime / legendary`.

Bereits vorbereitet, aber noch nicht persistent: `heat`, `prestige`, `police_pressure`, `scene_activity` je Bezirk. Unbekannte District-Overrides sowie Besitzangaben für nicht kaufbare Orte werden fail-closed abgewiesen.

### Hall of Tribute

Die Hall ist der feste Prestige-/Ranking-Ort. Für spätere Auszeichnungen sind bereits satirische Titel vorbereitet, z. B. **Lärmadel, Bunkerbaron, Kabelkönig, Pegelpapst, Stromheiland, Betonlegende und Nachtminister**.

Vertrag: [`manifests/CITY_MAP_MANIFEST.json`](manifests/CITY_MAP_MANIFEST.json) · [`docs/CRISIS_CITY_0.8.3-B.md`](docs/CRISIS_CITY_0.8.3-B.md)

---

## 🧭 Einstieg ohne Vorwissen

1. Spielidee: [`docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md`](docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md)
2. praktischer aktueller Einstieg: [`docs/SPIELERANLEITUNG.md`](docs/SPIELERANLEITUNG.md)
3. Entwicklergesamtbild: [`docs/SPIELBESCHREIBUNG_TECHNISCH.md`](docs/SPIELBESCHREIBUNG_TECHNISCH.md)
4. aktueller Entwicklungsblock: [`TODO.md`](TODO.md)

> [!NOTE]
> Der vorhandene HTML-Blueprint ist weiterhin schreibgeschützt. Die Berlin Ops Map besitzt bereits einen getesteten Projection-Vertrag, aber noch keinen fertigen grafischen Renderer oder Domain-Schreibweg.

### HTML-Blueprint starten

```bash
python3 tools/start_web_blueprint.py
```

Bei einem belegten Port:

```bash
python3 tools/start_web_blueprint.py --port 0
```

---

## 🗂️ Schnellzugriff

| Ich suche … | Dann hier entlang |
|---|---|
| vollständige Spielidee ohne Technik | [`docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md`](docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md) |
| technische Gesamtbeschreibung | [`docs/SPIELBESCHREIBUNG_TECHNISCH.md`](docs/SPIELBESCHREIBUNG_TECHNISCH.md) |
| Spieler-Einstieg | [`docs/SPIELERANLEITUNG.md`](docs/SPIELERANLEITUNG.md) |
| aktuellen Entwicklungsstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| nächste Aufgaben | [`TODO.md`](TODO.md) |
| Event State | [`docs/EVENT_STATE_0.8.1.md`](docs/EVENT_STATE_0.8.1.md) |
| Event Actions | [`manifests/EVENT_ACTION_MANIFEST.json`](manifests/EVENT_ACTION_MANIFEST.json) |
| Crisis + Berlin Map | [`docs/CRISIS_CITY_0.8.3-B.md`](docs/CRISIS_CITY_0.8.3-B.md) |
| Incident-Katalog | [`manifests/INCIDENT_MANIFEST.json`](manifests/INCIDENT_MANIFEST.json) |
| Berlin Ops Map | [`manifests/CITY_MAP_MANIFEST.json`](manifests/CITY_MAP_MANIFEST.json) |
| Architektur | [`docs/ARCHITEKTURVERTRAG.md`](docs/ARCHITEKTURVERTRAG.md) |
| Gameplay Actions | [`docs/GAMEPLAY_ACTION_CONTRACT.md`](docs/GAMEPLAY_ACTION_CONTRACT.md) |
| Persistence / Recovery | [`docs/PERSISTENCE_CONTRACT.md`](docs/PERSISTENCE_CONTRACT.md) · [`docs/RECOVERY_0.5.1.md`](docs/RECOVERY_0.5.1.md) |
| A4 / A3 | [`docs/A4_OPS_DECK_0.6.3.md`](docs/A4_OPS_DECK_0.6.3.md) · [`docs/A3_CINEMATIC_FORGE_0.6.4.md`](docs/A3_CINEMATIC_FORGE_0.6.4.md) |
| Repository Guard | [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) |
| `/safe-merge` | [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md) |
| Entwicklerübergabe | [`docs/ENTWICKLERHANDBUCH.md`](docs/ENTWICKLERHANDBUCH.md) |
| Änderungshistorie | [`CHANGELOG.md`](CHANGELOG.md) |

---

## 🧩 Architektur in 30 Sekunden

```text
Domain: CharacterState + EventState + EconomyState + IncidentState
  ↓
Application: Character / Event / Economy / Execution / Incident Services
  ↓
Persistence: Journal + State + Snapshot + Recovery
  ↓
Read-only Projections
  ├─→ Character / Feedback
  ├─→ Ranking
  └─→ Berlin Ops Map
  ↓
A4 / A3 / spätere Kartenansicht
```

| Bereich | Verantwortung | Grenze |
|---|---|---|
| `domain` | Charakter, Progression, Event, Economy, Incident-State | kennt keine UI/Infrastruktur |
| `application` | Use Cases, Commands, atomare Orchestrierung | umgeht Persistenz nicht |
| `infrastructure` | Journal, Save, Snapshot, Recovery | verwaltet keine sichtbaren UI-Texte |
| `presentation` | Projection, Komponenten, Inszenierung | schreibt Domain-/Save-State nicht direkt |
| `content` | sichtbare/lokalisierte Texte | ersetzt keine technischen Regeln |

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

- `repository-health` prüft JSON, Python-Struktur/Compile, Konfliktmarker, Informationskonsistenz, kanonische Symbole und Exporte.
- Guard-/CI-Sicherheitsdateien dürfen sich in normalen `/safe-merge`-PRs nicht selbst verändern.
- `Main Integrity` kontrolliert Änderungen auf `main`.
- native GitHub-Branch-Protection bleibt zusätzliche offene serverseitige Härtung.

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

### Action-Vertrag / Balance

```bash
python3 tools/validate_action_contract.py
python3 tools/simulate_characters/progression_simulator.py \
  --runs 1000 --days 720 --seed 90409 \
  --output reports/PROGRESSION_SIMULATION_0.4.1.json
```

Pull Requests nach `main` benötigen immer einen eindeutigen Status von Runtime Core, Presentation Core und Repository Health.

<details>
<summary><strong>📜 Wichtige Remote-Abnahmen</strong></summary>

- 0.7.2 / PR #41: Runtime Core `32533954380`, Presentation Core `32533954387`, Repository Health `32533954406`
- Safe-Merge-End-to-End / PR #38: Runtime Core `32528078989`, Presentation Core `32528078992`, Repository Health `32528078926`; `SAFE MERGE PASS`
- 0.8.1 / PR #48: Runtime Core `32537531324`, Presentation Core `32537531305`, Repository Health `32537531303`
- 0.8.2 Economy-Hardening / PR #61: Runtime Core `32557685040`, Presentation Core `32557685042`, Repository Health `32557685108`
- 0.8.3-A / PR #62: Runtime Core `32558175370`, Presentation Core `32558175365`, Repository Health `32558175382`; `SAFE MERGE PASS`
- 0.8.3-B / PR #63: Runtime Core `32559629560`, Presentation Core `32559629773`, Repository Health `32559629667`; 6 Review-Threads gelöst; `SAFE MERGE PASS`; Merge `816a3f1dd83d9396550d702c0ac85ba98ed069dd`

</details>

---

## 📚 Verbindliche Verträge

- [`docs/CHARACTER_FORGE.md`](docs/CHARACTER_FORGE.md)
- [`docs/PROGRESSION_CONTRACT.md`](docs/PROGRESSION_CONTRACT.md)
- [`docs/GAMEPLAY_ACTION_CONTRACT.md`](docs/GAMEPLAY_ACTION_CONTRACT.md)
- [`docs/EVENT_STATE_0.8.1.md`](docs/EVENT_STATE_0.8.1.md)
- [`manifests/EVENT_ACTION_MANIFEST.json`](manifests/EVENT_ACTION_MANIFEST.json)
- [`docs/CRISIS_CITY_0.8.3-B.md`](docs/CRISIS_CITY_0.8.3-B.md)
- [`manifests/INCIDENT_MANIFEST.json`](manifests/INCIDENT_MANIFEST.json)
- [`manifests/CITY_MAP_MANIFEST.json`](manifests/CITY_MAP_MANIFEST.json)
- [`docs/PERSISTENCE_CONTRACT.md`](docs/PERSISTENCE_CONTRACT.md)
- [`docs/RECOVERY_0.5.1.md`](docs/RECOVERY_0.5.1.md)
- [`docs/UI_UX_BLUEPRINT.md`](docs/UI_UX_BLUEPRINT.md)
- [`docs/PRESENTATION_CONTRACT_0.6.md`](docs/PRESENTATION_CONTRACT_0.6.md)
- [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md)
- [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md)

---

## 🔧 Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Normale PRs nach `main` werden ausschließlich über `/safe-merge` übernommen. Dafür müssen `runtime-core`, `presentation-core` und `repository-health` auf dem exakten PR-Head grün sein; der Branch muss den aktuellen `main` enthalten und alle Review-Threads müssen gelöst sein.

Details: [`AGENTS.md`](AGENTS.md) · [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) · [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md)
