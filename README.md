<div align="center">

# BUNKERFREQUENZ

### Beton. Bass. Berlin.

**Techno-/FreeTekno-Crew-RPG · Character Forge · Event-Management · Bunker-Entwicklung**

<p>
  <img alt="Runtime Baseline 0.5.2 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.5.2--alpha.1-ff4d00">
  <img alt="Character Forge 0.7.2 validiert" src="https://img.shields.io/badge/Character_Forge-0.7.2_validiert-7dff00">
  <img alt="Event State 0.8.1 remote validiert" src="https://img.shields.io/badge/Event_State-0.8.1_remote_validiert-f2c744">
  <img alt="Runtime Python Standardbibliothek" src="https://img.shields.io/badge/Runtime-Python_Standardbibliothek-00c2ff">
  <img alt="Mergeweg Safe Merge" src="https://img.shields.io/badge/Mergeweg-%2Fsafe--merge-8a2be2">
</p>

> **Entdecken → planen → handeln → eskalieren → auswerten → entwickeln.**  
> Verhalten, Training, Entscheidungen und Krisen formen die Crew – ohne starre Startklassen.

</div>

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

---

## ⚡ Projekt-Puls

| | Aktueller Stand |
|---|---|
| **Runtime-Baseline** | `0.5.2-alpha.1` |
| **Letzte remote validierte Feature-Stufe** | `0.8.1 – Event State Foundation` |
| **0.8.1-Abnahme** | PR #48 · Head `79cc26bec0a7...` · Runtime Core `32537531324`, Presentation Core `32537531305`, Repository Health `32537531303` grün |
| **Aktive Iteration** | `0.8.2 – Equipment & Economy` |
| **0.8.1-Abschluss** | PR #48 · Merge `9ed0dbd89280...` |
| **Weg zum ersten spielbaren Release** | `0.8.2 Economy → 0.8.3 Event-Loop → Release-Kandidat` |
| **Character Forge** | A4 Ops Deck + A3 Cinematic Forge auf derselben bestätigten Fachbasis |
| **Event Foundation** | Ort, Budgetrahmen, Acts, Crew, Equipment-Readiness, Zeitfenster, Sicherheit, Phasen und Revision |
| **Persistenz** | Journal, 60-Sekunden-Autosave, Snapshot, Recovery, kompensierender Undo |
| **Repository-Sicherheit** | `/safe-merge` + Main Integrity; native Branch Protection bleibt zusätzliche Härtung |
| **Grafischer Renderer** | auswertbarer statischer HTML-Blueprint vorhanden; noch kein schreibender Game-Client |
| **Telegram / Sync** | geplant; Transport-/Serverphase noch nicht implementiert |

> [!IMPORTANT]
> `VERSION.json` bezeichnet die letzte **versionierte Runtime-Baseline**. Feature-Meilensteine können weiter sein und werden getrennt in `PROJEKTSTATUS.json` und `TODO.md` geführt.

---

## 🚦 Was bis zum Release noch fehlt

Der aktuelle Stand ist eine validierte Spiellogik mit statischer, schreibgeschützter HTML-Auswertung – noch kein auslieferbarer Game-Client. Für das erste **spielbare Alpha-Release** sind drei Schritte verpflichtend:

1. **0.8.2 Equipment & Economy als einen Vertical Slice abnehmen:** Katalog, Besitz, Reservierung, Transaktionen und Recovery werden zusammen umgesetzt und bestätigt; es gibt keine fachliche Teilfreigabe.
2. **0.8.3 vollständiger Event-Loop:** Planung bis Abrechnung einschließlich Krisen, Folgen und A4/A3-Projektionen durchgängig spielbar machen.
3. **Release-Kandidat abnehmen:** Erst nach bestätigtem 0.8.3 den schreibenden A4-Client an die Runtime anbinden, dann Ersteinstieg, Start aus frischem Checkout und Save/Recovery-Smoke-Test nachweisen; danach erst Version und Release-Artefakt festlegen.

**Nicht blockierend für das erste lokale Alpha-Release:** Telegram-/Netzwerk-Sync und native GitHub-Branch-Protection. Beides bleibt wichtig, ist aber kein Bestandteil des lokalen Spielkerns.

Die prüfbaren Arbeitspakete und ihre Reihenfolge stehen in [`TODO.md`](TODO.md#p0--pflichtpfad-zum-ersten-spielbaren-alpha-release).

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
EVENT / KRISE / ENTSCHEIDUNG
   ↓
AUSWERTEN
   ↓
SKILLS · TRAITS · BIOGRAFIE · LEVEL · RESONANZ
   ↓
NEUE MÖGLICHKEITEN
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

### Character Forge

- 8 gemeinsame Komponenten
- A4 Ops Deck
- A3 Cinematic Forge
- bestätigtes Progressionsfeedback
- dynamische Biografie
- Reduced-Motion-Fallback
- Ranking / Network Foundation
- 20 Manifest-Actions mit Ressourcenwirkung

</td>
</tr>
</table>

### 0.7.2 verbindet den kompletten Character-Forge-Ablauf

```text
Action
  ↓
Energie / Stress
  ↓
Progression
  ↓
bestätigte Journal-Events
  ↓
Feedback + dynamische Biografie
  ↓
60-s-Autosave + Snapshot
  ↓
Undo nach erlaubter Kompensationsregel
  ↓
Reload / Recovery
  ↓
identische Projektion in A4 und A3
```

---

## 🏗️ 0.8.1 – Event State Foundation

0.8.1 setzt neben den Character-Zustand einen eigenen, journalfähigen `event`-Block. Character- und Eventdaten ersetzen sich beim Speichern nicht gegenseitig; Recovery kann beide Blöcke gemeinsam aus dem Journal rekonstruieren.

| Eventbereich | Vertrag in 0.8.1 |
|---|---|
| **Ort** | technische ID, Anzeigename, Region und Zugangsstatus |
| **Budget** | Event-Budgetrahmen in Cent; noch kein Zahlungsledger |
| **Acts** | geplant / bestätigt / abgesagt |
| **Crew** | Character-ID, Rolle und Verfügbarkeit |
| **Equipment** | Anforderung und Readiness; Besitz/Markt folgt in 0.8.2 |
| **Zeitfenster** | ISO-8601 mit UTC-Offset und Zeitzone |
| **Sicherheit** | `unreviewed`, `cleared`, `restricted`, `blocked` |
| **Revision** | monotone Revision; veraltete Schreibversuche werden abgewiesen |

```text
draft
  ↓
planning
  ↓
procurement
  ↓
transport
  ↓
setup
  ↓
soundcheck
  ↓
live ↔ crisis
  ↓       ↓
teardown ←
  ↓
settlement
  ↓
completed
```

> [!CAUTION]
> Ab `transport` verlangt der Domain-Vertrag einen gesetzten Ort, verifizierten Zugangsstatus, ein gültiges Zeitfenster und `safety_status=cleared`. Aus einem real klingenden Ortsnamen wird niemals automatisch eine Berechtigung abgeleitet.

Details: [`docs/EVENT_STATE_0.8.1.md`](docs/EVENT_STATE_0.8.1.md)

---

## 🧭 Einstieg ohne Vorwissen

**Du willst das Spielprinzip verstehen, ohne den Code zu kennen?**

1. Starte mit der [`Spieleranleitung`](docs/SPIELERANLEITUNG.md).
2. Lies danach bei Bedarf [`docs/GAME_SCHEMA.md`](docs/GAME_SCHEMA.md) für den Spiel-/Datenfluss.
3. [`A4 Ops Deck`](docs/A4_OPS_DECK_0.6.3.md) beschreibt den normalen Arbeitsablauf.
4. [`A3 Cinematic Forge`](docs/A3_CINEMATIC_FORGE_0.6.4.md) zeigt die stärker inszenierte Charakterentwicklung.
5. Für den neuen Eventzustand: [`Event State Foundation 0.8.1`](docs/EVENT_STATE_0.8.1.md).
6. Der nächste Entwicklungsblock steht kompakt in [`TODO.md`](TODO.md).

> [!NOTE]
> Der statische HTML-Blueprint lässt sich bereits lokal prüfen und anklicken. Er zeigt die Originalgrafik unverändert, wertet den UI-Vertrag aus und schreibt keine Spieldaten. Ein vollständiger grafischer Game-Client ist das noch nicht.

### HTML-Blueprint vollautomatisch starten

```bash
python3 tools/start_web_blueprint.py
```

Die Startroutine prüft zuerst alle benötigten Dateien, bindet den lokalen Server ohne fehleranfällige Vorabreservierung, zeigt Adresse und Stopp-Befehl sofort an und öffnet den Standardbrowser. Für einen rein manuellen Browserstart dient `--no-browser`; bei einem belegten Port nennt die Fehlermeldung mit `--port 0` direkt den automatischen Ausweg. Die Oberfläche führt zusätzlich einen kopierbaren Prüfbericht unter **Diagnose**.

---

## 🗂️ Schnellzugriff

| Ich suche … | Dann hier entlang |
|---|---|
| Spieler-Einstieg | [`docs/SPIELERANLEITUNG.md`](docs/SPIELERANLEITUNG.md) |
| HTML-Blueprint starten | `python3 tools/start_web_blueprint.py` |
| aktuellen Entwicklungsstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| nächste Aufgaben | [`TODO.md`](TODO.md) |
| Event State 0.8.1 | [`docs/EVENT_STATE_0.8.1.md`](docs/EVENT_STATE_0.8.1.md) |
| Architektur und Grenzen | [`docs/ARCHITEKTURVERTRAG.md`](docs/ARCHITEKTURVERTRAG.md) |
| Spiel-/Datenfluss | [`docs/GAME_SCHEMA.md`](docs/GAME_SCHEMA.md) |
| Character Forge | [`docs/CHARACTER_FORGE.md`](docs/CHARACTER_FORGE.md) |
| Gameplay Actions | [`docs/GAMEPLAY_ACTION_CONTRACT.md`](docs/GAMEPLAY_ACTION_CONTRACT.md) |
| Persistence / Recovery | [`docs/PERSISTENCE_CONTRACT.md`](docs/PERSISTENCE_CONTRACT.md) · [`docs/RECOVERY_0.5.1.md`](docs/RECOVERY_0.5.1.md) |
| A4 Ops Deck | [`docs/A4_OPS_DECK_0.6.3.md`](docs/A4_OPS_DECK_0.6.3.md) |
| A3 Cinematic Forge | [`docs/A3_CINEMATIC_FORGE_0.6.4.md`](docs/A3_CINEMATIC_FORGE_0.6.4.md) |
| Ranking / Network | [`docs/RANKING_NETWORK_0.6.5.md`](docs/RANKING_NETWORK_0.6.5.md) |
| Repository Guard | [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) |
| `/safe-merge` bedienen | [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md) |
| Datei finden | [`docs/REPOSITORY_INDEX.md`](docs/REPOSITORY_INDEX.md) |
| als Entwickler übernehmen | [`docs/ENTWICKLERHANDBUCH.md`](docs/ENTWICKLERHANDBUCH.md) |
| Änderungshistorie | [`CHANGELOG.md`](CHANGELOG.md) |

---

## 🧩 Architektur in 30 Sekunden

```text
Domain: CharacterState + EventState
  ↓
Application: Character-/Event-Services
  ↓
Persistence / bestätigte Events
  ↓
Character Projection + Feedback
  ↓
PresentationState
  ↓
8 gemeinsame Komponenten
  ├─→ A4 Ops Deck
  ├─→ A3 Cinematic Forge
  └─→ Ranking / Network
```

| Bereich | Verantwortung | Grenze |
|---|---|---|
| `domain` | Charakter, Progression, Traits, Eventzustand | kennt keine UI/Infrastruktur |
| `application` | Use Cases, Commands, Capabilities, State-Block-Koordination | umgeht Persistenz nicht |
| `infrastructure` | Journal, Save, Snapshot, Recovery | verwaltet keine sichtbaren UI-Texte |
| `presentation` | Projection, Komponenten, Inszenierung | schreibt Domain-/Save-State nicht direkt |
| `content` | sichtbare/lokalisierte Texte | ersetzt keine technischen Regeln |

---

## 🛡️ Repository-Sicherheit

Normale Änderungen nach `main` folgen diesem Pfad:

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
Main-Provenienz prüfen
   ↓
SAFE MERGE PASS
```

Zusätzlich gilt:

- alte versionsgebundene Feature-Branches werden fail-closed blockiert
- `repository-health` prüft JSON, Python-Compile/Struktur, Konfliktmarker, Informationskonsistenz, kanonische Symbole und Exporte
- Guard-/CI-Sicherheitsdateien dürfen sich in normalen `/safe-merge`-PRs nicht selbst verändern
- `Main Integrity` kontrolliert Änderungen auf `main`
- GitHub-Eventual-Consistency erhält nur beim Lesen der Provenienz begrenzte Retries; der Merge wird **nie wiederholt**
- native GitHub-Branch-Protection ist weiterhin eine zusätzliche offene serverseitige Härtung

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

Fachliche Prüfungen bleiben risikobasiert. Pull Requests nach `main` benötigen jedoch immer einen eindeutigen Status von Runtime Core, Presentation Core und Repository Health.

<details>
<summary><strong>📜 Bisherige Remote-Abnahmen anzeigen</strong></summary>

- 0.6.3 / PR #28: Runtime Core `32514970109`, Presentation Core `32514970398`
- 0.6.4 / PR #29: Runtime Core `32516833552`, Presentation Core `32516833514`
- 0.6.5 / PR #30: Runtime Core `32517683276`, Presentation Core `32517683263`
- 0.7.1 / PR #31: Runtime Core `32519042006`, Presentation Core `32519041908`
- Repository Guard / PR #34: Runtime Core `32522887448`, Presentation Core `32522887380`, Repository Health `32522887383`
- Safe-Merge-Bootstrap / PR #35: Runtime Core `32527116025`, Presentation Core `32527115999`, Repository Health `32527116022`
- Eventual-Consistency-Hotfix / PR #37: Runtime Core `32527882811`, Presentation Core `32527882838`, Repository Health `32527882791`
- Safe-Merge-End-to-End / PR #38: Runtime Core `32528078989`, Presentation Core `32528078992`, Repository Health `32528078926`; `SAFE MERGE PASS`
- Safety Receipt / PR #39: Runtime Core `32528915005`, Presentation Core `32528914997`, Repository Health `32528915004`; `SAFE MERGE PASS`
- 0.7.2 / PR #41, validierter Head `5f7ded400a5f...`: Runtime Core `32533954380`, Presentation Core `32533954387`, Repository Health `32533954406`
- 0.7.2 Closeout / PR #45: Runtime Core `32534969250`, Presentation Core `32534969199`, Repository Health `32534969209`; `SAFE MERGE PASS`
- Integrity-Reparatur / PR #47: Runtime Core `32536504014`, Presentation Core `32536504089`, Repository Health `32536504068`; `SAFE MERGE PASS`
- 0.8.1 / PR #48, initial validierter Head `79cc26bec0a7...`: Runtime Core `32537531324`, Presentation Core `32537531305`, Repository Health `32537531303`

Der versehentliche PR #32 wurde trotz roter Compile-Gates gemergt und durch Reparatur-PR #33 aus dem kanonischen Baum entfernt. Spätere direkte `main`-Änderungen wurden vom Main-Integrity-Guard erkannt und über validierte PRs bereinigt. Repository Guard und `/safe-merge` bleiben der vorgeschriebene normale Mergeweg.

</details>

---

## 📚 Verbindliche Verträge

- [`docs/CHARACTER_FORGE.md`](docs/CHARACTER_FORGE.md)
- [`docs/PROGRESSION_CONTRACT.md`](docs/PROGRESSION_CONTRACT.md)
- [`docs/GAMEPLAY_ACTION_CONTRACT.md`](docs/GAMEPLAY_ACTION_CONTRACT.md)
- [`docs/EVENT_STATE_0.8.1.md`](docs/EVENT_STATE_0.8.1.md)
- [`docs/CHARACTER_CORE_0.5.md`](docs/CHARACTER_CORE_0.5.md)
- [`docs/PERSISTENCE_CONTRACT.md`](docs/PERSISTENCE_CONTRACT.md)
- [`docs/RECOVERY_0.5.1.md`](docs/RECOVERY_0.5.1.md)
- [`docs/UI_UX_BLUEPRINT.md`](docs/UI_UX_BLUEPRINT.md)
- [`docs/PRESENTATION_CONTRACT_0.6.md`](docs/PRESENTATION_CONTRACT_0.6.md)
- [`docs/A4_OPS_DECK_0.6.3.md`](docs/A4_OPS_DECK_0.6.3.md)
- [`docs/A3_CINEMATIC_FORGE_0.6.4.md`](docs/A3_CINEMATIC_FORGE_0.6.4.md)
- [`docs/RANKING_NETWORK_0.6.5.md`](docs/RANKING_NETWORK_0.6.5.md)
- [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md)
- [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md)
- [`docs/DATENMODELL.md`](docs/DATENMODELL.md)

---

## 🔧 Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Parallelimplementierungen derselben kanonischen Datei werden nicht weitergeführt. Normale PRs nach `main` werden ausschließlich über `/safe-merge` übernommen. Dafür müssen `runtime-core`, `presentation-core` und `repository-health` auf dem exakten PR-Head grün sein; der Branch muss den aktuellen `main` enthalten und alle Review-Threads müssen gelöst sein.

Details: [`AGENTS.md`](AGENTS.md) · [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) · [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md)
