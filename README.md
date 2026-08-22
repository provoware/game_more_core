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
| **Letzte remote validierte Feature-Stufe** | `0.8.4 – Schreibender A4-Game-Client + First-Run/Recovery` |
| **0.8.4-Abnahme** | PR #69 · Head `3d61e9d6385a...` · Runtime Core `32575062624`, Presentation Core `32575062602`, Repository Health `32575062620` grün · 0 ungelöste Review-Threads · `SAFE MERGE PASS` · Merge `28459c197489...` |
| **Release-Abnahme** | PR #72 · Head `7fe1a39c6b69...` · Runtime Core `32576362896`, Presentation Core `32576362890`, Repository Health `32576362810`, Release Acceptance `32576362827` grün · `SAFE MERGE PASS` · Merge `72bb30242727...` |
| **Aktiver Release-Kandidat** | `0.8.4-alpha.1` · reproduzierbares ZIP + SHA-256 + entpackter Paket-Smoke auf PR #73 |
| **0.8.3-A** | 8 kanonische Event-Aktionen und zentrale Blocker-/Voraussetzungslogik |
| **0.8.3-B** | Crisis Engine + Berlin Ops Map Foundation |
| **0.8.3-C** | atomare Abrechnung, Budget/Stress/Ruf, Biografie, `event.completed`, Recovery |
| **0.8.4** | lokaler schreibender A4-Client, First Run, kompletter Event-Smoke, Save/Restart/Recovery |
| **Character Forge** | schreibender A4-Client + A4 Ops Deck + A3 Cinematic Forge auf derselben bestätigten Fachbasis |
| **Persistenz** | append-only Journal, 60-Sekunden-Autosave, Snapshot, Recovery, kompensierender Undo; fehlender State bei gültigem Head-Snapshot regressionsgehärtet |
| **Repository-Sicherheit** | `/safe-merge` + Main Integrity; native Branch Protection bleibt zusätzliche Härtung |
| **Grafischer Renderer** | A4 lokaler Game-Client vorhanden; Berlin Ops Map weiter als getestete read-only Projection, noch kein hochwertiger Kartenrenderer |
| **Telegram / Sync** | geplant; Transport-/Serverphase noch nicht implementiert |

> [!IMPORTANT]
> `0.8.4-alpha.1` ist die erste lokal spielbare Runtime-Baseline. Sie wurde erst nach der separaten frischen-Checkout-Release-Abnahme festgelegt. Der Release-PR muss zusätzlich das reproduzierbare Paket samt SHA-256 und den entpackten Paket-Smoke auf seinem finalen Head bestätigen.

---

## 🚦 Release-Status

Der fachliche Event-Loop **und der kleinste schreibende A4-Client** sind vollständig remote validiert. Die separate Release-Abnahme aus einem frischen Checkout ist ebenfalls abgeschlossen: realer Launcherprozess, freie Portwahl, Fehlerpfade, Save/Restart und Recovery sind geprüft.

Für `0.8.4-alpha.1` läuft deshalb nur noch die Paket-/Merge-Qualifikation:

1. **Byte-reproduzierbares ZIP:** derselbe Source-Head muss zweimal exakt dieselben ZIP-Bytes erzeugen.
2. **SHA-256:** Paket und Sidecar müssen denselben Digest bestätigen.
3. **Entpackter Paket-Smoke:** `START_BUNKERFREQUENZ.sh` aus einem frischen Zielordner starten, First Run bis `completed` ausführen und Checkpoint bestätigen.
4. **Finaler Release-Head:** Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package müssen gemeinsam grün sein; danach ausschließlich `/safe-merge`.

**Nicht blockierend für das erste lokale Alpha:** Telegram-/Netzwerk-Sync, öffentlicher Serverbetrieb, persistente Bezirksdynamik, Immobilienausbau, Hall-of-Tribute-Saisons und native GitHub-Branch-Protection.

Die genaue Reihenfolge steht in [`TODO.md`](TODO.md#release-abnahme--erstes-lokales-alpha-).

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
- 60-Sekunden-Autosave
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
- `completed` wird ausschließlich über den validierten 0.8.3-C-Settlement-Service erzeugt

Maschinenlesbarer Vertrag: [`manifests/EVENT_ACTION_MANIFEST.json`](manifests/EVENT_ACTION_MANIFEST.json)

---

## 🚨 0.8.3-B1 – Crisis / Incident Engine ✅

Ein laufendes Event kann tatsächlich eskalieren. Die Krise ist kein UI-Effekt, sondern eigener persistierter Zustand.

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

Krisen erzeugen bestätigte Folgen auf Budget, Ruf, Crew-Stress, Stabilität und Heat. Diese stehen im `IncidentState.pending_settlement` und werden nicht direkt auf Economy oder Character geschrieben. Damit bleibt die 0.8.2-Regel erhalten: Geld ändert sich nur über bestätigte Economy-Transaktionen. Der validierte 0.8.3-C-Service übernimmt diese Folgen anschließend genau einmal.

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

## 💰 0.8.3-C – Settlement & Consequences ✅

0.8.3-C schließt den fachlichen Event-Loop. Aus `settlement` wird `completed` erst, wenn bestätigte Folgen gemeinsam verbucht und dauerhaft bestätigt sind.

```text
settlement
  ↓
Budget über Economy-Ledger
  ↓
Stress + Ruf über Character-Events
  ↓
Biografie dem bestätigten Character zuordnen
  ↓
event.phase_changed
  ↓
event.completed + SettlementState
```

Wesentliche Garantien:

- vollständiger Abschluss in **einem atomaren Persistence-Commit**
- Event ohne Krise ist gültig; fehlender Incident-State wird deterministisch als leer behandelt
- `pending_settlement` wird genau einmal verbraucht
- negatives Endbudget wird abgewiesen; kein erfundenes Schuldenmodell
- Stress bleibt `0..100`
- ältere Saves mit früher zulässigem negativem Ruf bleiben lesbar
- neue Settlement-Ergebnisse normalisieren Ruf auf mindestens `0`, damit Ranking kompatibel bleibt
- Budget-, Stress- und Ruf-Deltas im Receipt müssen exakt zu den bestätigten Effekten passen
- Biografieeintrag trägt die bestätigte Character-ID
- Heat/Stabilität bleiben bestätigte Settlement-Ergebnisse und werden noch nicht als District-State geschrieben
- `event.completed` kann nicht über den allgemeinen Event-Service umgangen werden
- Crash nach durablem Journal ist über Combined Recovery vollständig rekonstruierbar

Remote-Abnahme: PR #65 · Head `ccfb145547b241a179bd0135d34a7470d690821c` · Runtime Core `32568683844` · Presentation Core `32568683898` · Repository Health `32568683863` · 0 ungelöste Review-Threads · `SAFE MERGE PASS` · Merge `5ae811333878ae67947417ccb72e791caafe4ba9`.

Vertrag: [`docs/SETTLEMENT_0.8.3-C.md`](docs/SETTLEMENT_0.8.3-C.md) · [`manifests/SETTLEMENT_MANIFEST.json`](manifests/SETTLEMENT_MANIFEST.json) · [`reports/SETTLEMENT_VALIDATION_0.8.3-C.json`](reports/SETTLEMENT_VALIDATION_0.8.3-C.json)

---

## 🎮 0.8.4 – Schreibender A4-Game-Client ✅

0.8.4 macht aus dem gehärteten Fachkern erstmals einen kleinen lokalen Spielclient. Die zentrale Regel bleibt erhalten: **Der Browser besitzt keine zweite Spiellogik.**

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

- Command-Allowlist und strikte erlaubte Felder; unerwartete Eingaben werden vor dem Write abgewiesen
- Eventbuttons und Blocker stammen direkt aus der vorhandenen Runtime-Availability
- Browser stellt kanonische Blocker-IDs in verständlichem Deutsch dar, berechnet die Regeln aber nicht selbst
- lokaler Server bindet nur an `127.0.0.1` und liefert statisch ausschließlich `web/a4/` aus
- First Run kann Character/Event/Economy nur auf einem leeren GENESIS-Stand anlegen und überschreibt keinen vorhandenen Save
- manueller Snapshot/Checkpoint und normaler Neustart verwenden denselben persistierten Zustand
- automatisierter End-to-End-Smoke deckt den kompletten Eventpfad einschließlich optionaler Krise, Settlement, Neustart und Recovery ab
- der Smoke fand einen echten Recovery-Randfall: ein gültiger Snapshot am Journal-Head darf einen fehlenden `state/current.json` nicht als gesund tarnen; der Persistence-Kern stellt ihn nun korrekt wieder her
- die Recovery-Regel besitzt eine eigene Regression und der strenge Smoke wurde nicht abgeschwächt

Remote-Abnahme: PR #69 · Head `3d61e9d6385a0b79069132df24d655fef42b0451` · Runtime Core `32575062624` · Presentation Core `32575062602` · Repository Health `32575062620` · 0 ungelöste Review-Threads · `SAFE MERGE PASS` · Merge `28459c197489577923fadeb5f0a42d1ac1e39327`.

Start-/Spielanleitung: [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md) · technischer Vertrag: [`docs/A4_WRITING_CLIENT_0.8.4.md`](docs/A4_WRITING_CLIENT_0.8.4.md) · Evidence: [`reports/A4_CLIENT_VALIDATION_0.8.4.json`](reports/A4_CLIENT_VALIDATION_0.8.4.json)

---

## 🧭 Einstieg ohne Vorwissen

1. Spielidee: [`docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md`](docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md)
2. **A4-First-Run Schritt für Schritt:** [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md)
3. allgemeiner Spieler-Einstieg: [`docs/SPIELERANLEITUNG.md`](docs/SPIELERANLEITUNG.md)
4. Entwicklergesamtbild: [`docs/SPIELBESCHREIBUNG_TECHNISCH.md`](docs/SPIELBESCHREIBUNG_TECHNISCH.md)
5. aktueller Entwicklungsblock: [`TODO.md`](TODO.md)

> [!NOTE]
> Der ältere HTML-Blueprint unter `web/` bleibt bewusst **schreibgeschützt und getrennt**. Der neue lokale A4-Game-Client befindet sich in `web/a4/` und schreibt ausschließlich über die Application-Grenze. Die Berlin Ops Map besitzt weiterhin einen getesteten read-only Projection-Vertrag, aber noch keinen hochwertigen Kartenrenderer oder eigenen Domain-Schreibweg.

### Schreibenden A4-Game-Client starten

```bash
./START_BUNKERFREQUENZ.sh
```

Alternativ direkt über Python:

```bash
python3 tools/start_a4_game_client.py
```

Bei einem belegten Port bzw. für automatische freie Portwahl:

```bash
./START_BUNKERFREQUENZ.sh --port 0
```

Der alte schreibgeschützte Blueprint bleibt separat startbar:

```bash
python3 tools/start_web_blueprint.py
```

---

## 🗂️ Schnellzugriff

| Ich suche … | Dann hier entlang |
|---|---|
| vollständige Spielidee ohne Technik | [`docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md`](docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md) |
| technische Gesamtbeschreibung | [`docs/SPIELBESCHREIBUNG_TECHNISCH.md`](docs/SPIELBESCHREIBUNG_TECHNISCH.md) |
| A4 First Run | [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md) |
| A4 Schreibgrenze | [`docs/A4_WRITING_CLIENT_0.8.4.md`](docs/A4_WRITING_CLIENT_0.8.4.md) |
| Spieler-Einstieg | [`docs/SPIELERANLEITUNG.md`](docs/SPIELERANLEITUNG.md) |
| aktuellen Entwicklungsstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| nächste Aufgaben | [`TODO.md`](TODO.md) |
| Event State | [`docs/EVENT_STATE_0.8.1.md`](docs/EVENT_STATE_0.8.1.md) |
| Event Actions | [`manifests/EVENT_ACTION_MANIFEST.json`](manifests/EVENT_ACTION_MANIFEST.json) |
| Crisis + Berlin Map | [`docs/CRISIS_CITY_0.8.3-B.md`](docs/CRISIS_CITY_0.8.3-B.md) |
| Incident-Katalog | [`manifests/INCIDENT_MANIFEST.json`](manifests/INCIDENT_MANIFEST.json) |
| Settlement | [`docs/SETTLEMENT_0.8.3-C.md`](docs/SETTLEMENT_0.8.3-C.md) · [`manifests/SETTLEMENT_MANIFEST.json`](manifests/SETTLEMENT_MANIFEST.json) |
| Berlin Ops Map | [`manifests/CITY_MAP_MANIFEST.json`](manifests/CITY_MAP_MANIFEST.json) |
| Architektur | [`docs/ARCHITEKTURVERTRAG.md`](docs/ARCHITEKTURVERTRAG.md) |
| Gameplay Actions | [`docs/GAMEPLAY_ACTION_CONTRACT.md`](docs/GAMEPLAY_ACTION_CONTRACT.md) |
| Persistence / Recovery | [`docs/PERSISTENCE_CONTRACT.md`](docs/PERSISTENCE_CONTRACT.md) · [`docs/RECOVERY_0.5.1.md`](docs/RECOVERY_0.5.1.md) |
| A4 / A3 Presentation | [`docs/A4_OPS_DECK_0.6.3.md`](docs/A4_OPS_DECK_0.6.3.md) · [`docs/A3_CINEMATIC_FORGE_0.6.4.md`](docs/A3_CINEMATIC_FORGE_0.6.4.md) |
| Repository Guard | [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) |
| `/safe-merge` | [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md) |
| Entwicklerübergabe | [`docs/ENTWICKLERHANDBUCH.md`](docs/ENTWICKLERHANDBUCH.md) |
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

| Bereich | Verantwortung | Grenze |
|---|---|---|
| `domain` | Charakter, Progression, Event, Economy, Incident, Settlement | kennt keine UI/Infrastruktur |
| `application` | Use Cases, Commands, atomare Orchestrierung, GameClientSession-Routing | umgeht Persistenz nicht; dupliziert keine Domainregeln |
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
- 0.8.3-C / PR #65: Runtime Core `32568683844`, Presentation Core `32568683898`, Repository Health `32568683863`; 0 ungelöste Review-Threads; `SAFE MERGE PASS`; Merge `5ae811333878ae67947417ccb72e791caafe4ba9`
- Repository-Hygiene / PR #67: Runtime Core `32568910870`, Presentation Core `32568910892`, Repository Health `32568910865`; `SAFE MERGE PASS`; Merge `057b5131dfd5bfaf1c26ddd0a3e862fb52c0675f`
- 0.8.4 A4 Game Client / PR #69: Runtime Core `32575062624`, Presentation Core `32575062602`, Repository Health `32575062620`; 0 ungelöste Review-Threads; `SAFE MERGE PASS`; Merge `28459c197489577923fadeb5f0a42d1ac1e39327`
- Release Acceptance / PR #72: Runtime Core `32576362896`, Presentation Core `32576362890`, Repository Health `32576362810`, Release Acceptance `32576362827`; `SAFE MERGE PASS`; Merge `72bb3024272797b27632a96559ae8abb665fff8a`

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
- [`docs/SETTLEMENT_0.8.3-C.md`](docs/SETTLEMENT_0.8.3-C.md)
- [`manifests/SETTLEMENT_MANIFEST.json`](manifests/SETTLEMENT_MANIFEST.json)
- [`docs/A4_WRITING_CLIENT_0.8.4.md`](docs/A4_WRITING_CLIENT_0.8.4.md)
- [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md)
- [`reports/A4_CLIENT_VALIDATION_0.8.4.json`](reports/A4_CLIENT_VALIDATION_0.8.4.json)
- [`reports/RELEASE_ACCEPTANCE_ALPHA.json`](reports/RELEASE_ACCEPTANCE_ALPHA.json)
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