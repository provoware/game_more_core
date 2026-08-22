<div align="center">

# BUNKERFREQUENZ

### Beton. Bass. Berlin.

**Techno-/FreeTekno-Crew-RPG · Character Forge · Event-Management · Bunker-Entwicklung**

<p>
  <img alt="Runtime Baseline 0.8.4 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.8.4--alpha.1-ff4d00">
  <img alt="Feature Stand 0.8.5 E validiert" src="https://img.shields.io/badge/Feature_Stand-0.8.5--E_validiert-7dff00">
  <img alt="Economy 0.8.2 remote validiert" src="https://img.shields.io/badge/Economy-0.8.2_remote_validiert-f2c744">
  <img alt="Settlement 0.8.3 C remote validiert" src="https://img.shields.io/badge/Settlement-0.8.3--C_remote_validiert-2ee6a6">
  <img alt="A4 Game Client 0.8.4 remote validiert" src="https://img.shields.io/badge/A4_Game_Client-0.8.4_remote_validiert-ff7ad9">
  <img alt="Living Districts 0.8.5 D validiert" src="https://img.shields.io/badge/Living_Districts-0.8.5--D_validiert-00c2ff">
  <img alt="Hall of Tribute 0.8.5 E validiert" src="https://img.shields.io/badge/Hall_of_Tribute-0.8.5--E_validiert-e840ff">
  <img alt="First Playable Alpha 0.8.4 alpha 1" src="https://img.shields.io/badge/First_Playable_Alpha-0.8.4--alpha.1-7dff00">
  <img alt="Mergeweg Safe Merge" src="https://img.shields.io/badge/Mergeweg-%2Fsafe--merge-8a2be2">
</p>

> **Entdecken → planen → handeln → eskalieren → entscheiden → abrechnen → Welt verändern → aufsteigen.**  
> Verhalten, Training, Entscheidungen, Straßenleben und Events formen Crew und Stadt – ohne starre Startklassen.

</div>

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

---

## ⚡ Projekt-Puls

| | Aktueller Stand |
|---|---|
| **Runtime-Baseline** | `0.8.4-alpha.1` – weiterhin letzter bewusst freigegebener Produktrelease |
| **Validierter Feature-Stand auf main** | ✅ `0.8.5-E` · Competitive Ranking, Personalisierung, Street Encounters, Living Districts und Hall of Tribute |
| **Erstes lokal spielbares Alpha** | ✅ `0.8.4-alpha.1` remote validiert, reproduzierbar paketiert und per `/safe-merge` übernommen |
| **Release-Artefakt** | `BUNKERFREQUENZ-0.8.4-alpha.1.zip` · SHA-256 `fccf16ee3728827ba4eba0dfd0e3cbaf844dd68c382b3c29c766f94a7ef85146` · byte-reproduzierbar · entpackter Paket-Smoke bis `completed` |
| **0.8.5-A** | Competitive Top-10 ohne Ranggleichstände; Momentum verdrängt bei Wertgleichstand |
| **0.8.5-B** | Anzeigename, Alias, Spitznamen und Motto im A4-Client editierbar |
| **0.8.5-C** | replaybare Street Encounters · 60 % positiv / 25 % ruhig / 15 % negativ |
| **0.8.5-D** | persistente Bezirkslage: Heat, Prestige, Polizeidruck, Szeneaktivität · Settlement/Street → Journal → Recovery |
| **0.8.5-E** | Hall of Tribute im A4-Client · Ruf/Level/Resonanz · Top 10 · Auf-/Abstieg · keine erfundenen Gegner |
| **Nächster Entwicklungsblock** | `0.8.6-A – Property Purchase Foundation`: die 7 katalogisierten kaufbaren Orte ausschließlich über bestätigte Economy-Transaktionen erwerbbar machen |
| **Character Forge** | schreibender A4-Client + A4 Ops Deck + A3 Cinematic Forge auf derselben bestätigten Fachbasis |
| **Persistenz** | append-only Journal, 60-Sekunden-Autosave, Snapshot, Recovery, kompensierender Undo; District-State ist in Combined Recovery integriert |
| **Repository-Sicherheit** | `/safe-merge` + Main Integrity; native Branch Protection bleibt zusätzliche Härtung |
| **Grafischer Renderer** | A4 lokaler Game-Client vorhanden; Berlin Ops Map besitzt dynamische read-only District-Werte, hochwertiger Kartenrenderer folgt später |
| **Telegram / Sync** | geplant; Transport-/Serverphase noch nicht implementiert; Hall erfindet deshalb keine Netzwerkgegner |

> [!IMPORTANT]
> `0.8.4-alpha.1` bleibt die erste **freigegebene lokal spielbare Runtime-Baseline**. Die anschließend gemergten und remote validierten 0.8.5-A–E-Features ändern diese Produktversion bewusst nicht stillschweigend. Ein neuer Release benötigt eine eigene Release-Abnahme.

---

## 🚦 Release- und Feature-Status ✅

Der fachliche Event-Loop, der schreibende A4-Client und die separate Release-Abnahme aus einem frischen Checkout sind abgeschlossen. `0.8.4-alpha.1` wurde auf PR #73 als reproduzierbares Release-Paket qualifiziert und ausschließlich per `/safe-merge` übernommen.

Finaler Release-Head `ece6c145bb07dbb2eb87170887374c4124a871f1`:

1. **Runtime Core:** `32576855723` ✅
2. **Presentation Core:** `32576855749` ✅
3. **Repository Health:** `32576855738` ✅
4. **Release Acceptance:** `32576855720` ✅
5. **Release Package:** `32576855768` ✅
6. **Review-Threads:** `0` offen
7. **Safe Merge:** PASS · Merge `3fdb5cc3d57e73734d1f594603cafdd6d06c5210`

Das Spiel-ZIP `BUNKERFREQUENZ-0.8.4-alpha.1.zip` besitzt SHA-256 `fccf16ee3728827ba4eba0dfd0e3cbaf844dd68c382b3c29c766f94a7ef85146`. Der Paket-Gate baut das ZIP zweimal byte-identisch, entpackt es in einen frischen Zielordner, startet `START_BUNKERFREQUENZ.sh`, prüft HTTP-Health, spielt den Kernpfad bis `completed` und erzeugt anschließend einen Checkpoint.

### Danach sicher gemergter Feature-Ausbau 0.8.5

| Stufe | Inhalt | Merge |
|---|---|---|
| **0.8.5-A** | Competitive Displacement Ranking | `b41d8f416679515307f2a580fb66b0569057836a` |
| **0.8.5-B** | A4-Profilpersonalisierung | `5a9eed536d48f30cdd1f4569e9e1b1724e5ced80` |
| **0.8.5-C** | Replaybare Street Encounters | `38de9f42c2908d63945db7bf25277b2f940ede6e` |
| **0.8.5-D** | Living Districts | `98c8b84715cc308dd1bc9fd92b7c7e56a35cc861` |
| **0.8.5-E** | Hall of Tribute / sichtbare Top 10 | `d383a3f364c6ee8cd954041f1d324e0ace0cb357` |

**Noch bewusst nicht Bestandteil:** Telegram-/Netzwerk-Sync, öffentlicher Serverbetrieb, Immobilienkauf/-ausbau, saisonale Hall-Zyklen und nativer GitHub-Branch-Schutz.

Maschinenlesbarer Release-Nachweis: [`reports/RELEASE_0.8.4-alpha.1.json`](reports/RELEASE_0.8.4-alpha.1.json) · aktueller Feature-Stand: [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json)

---

## 🎛️ Der Kern des Spiels

```text
ENTDECKEN / STRASSE
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
HEAT · PRESTIGE · POLIZEIDRUCK · SZENEAKTIVITÄT
   ↓
HALL OF TRIBUTE / TOP 10
   ↓
NEUE ORTE / IMMOBILIEN / MÖGLICHKEITEN
```

### Was Charaktere und Welt wirklich verändert

- **16 Skills** statt fester Klassen
- **165 individuelle Trait-Namen** über 15 gemeinsame Effektfamilien
- Training, Praxis, Krisen, Teamplay, Erkundung, Erfolg und Scheitern erzeugen unterschiedliche Evidenz
- Spezialisierungen entstehen aus dauerhaftem Verhalten – nicht aus einer Klassenwahl
- Level 1–50 gehen anschließend in **offene Resonanzränge** über
- dynamische Biografie entsteht ausschließlich aus bestätigten Journal-Ereignissen
- Street Encounters sind deterministisch und können nicht durch Reload neu gewürfelt werden
- bestätigte Settlements und Street Encounters verändern die persistente Bezirkslage
- Ranglistenwerte werden projiziert; der Browser sortiert oder erfindet keine Konkurrenz

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
- replaybare Street Encounters

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
- Combined Recovery einschließlich District-State

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
- persistente Living Districts
- Hall of Tribute mit sichtbarer Top 10
- 7 katalogisierte kaufbare Orte als Grundlage für 0.8.6-A

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

## 🗺️ 0.8.3-B2 + 0.8.5-D – Berlin Ops Map & Living Districts ✅

Die Welt besitzt eine eigene Handlungsebene. Sie ist ausdrücklich **stilisierte Spielkarte, keine Navigation**: 0–100-Koordinaten statt realer Adresslogik machen sie offline, portabel und rendererunabhängig.

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

Seit 0.8.5-D sind `heat`, `prestige`, `police_pressure` und `scene_activity` je Bezirk **persistent**. Sie entstehen ausschließlich aus bestätigten Settlement- bzw. Street-Quellen, werden auf `0..100` begrenzt, besitzen stabile Source-IDs und werden durch Combined Recovery rekonstruiert. Ein unbekannter Ort erzeugt einen sicheren No-op statt einer erfundenen Bezirkszuordnung.

### Hall of Tribute

Die Hall ist seit 0.8.5-E sichtbarer Prestige-/Ranking-Ort im A4-Client. Sofort verfügbare lokale Modi sind **Ruf, Level und Resonanz**. Das bestehende Competitive-Displacement-Ranking liefert eindeutige Plätze und Bewegungen. Ohne bestätigte weitere Teilnehmer werden keine Gegner oder Netzwerkwerte erfunden.

Saisonale Titel wie **Lärmadel, Bunkerbaron, Kabelkönig, Pegelpapst, Stromheiland, Betonlegende und Nachtminister** bleiben bewusst ein späterer, eigener Zeitzyklus-Ausbau.

Verträge: [`manifests/CITY_MAP_MANIFEST.json`](manifests/CITY_MAP_MANIFEST.json) · [`manifests/DISTRICT_STATE_MANIFEST.json`](manifests/DISTRICT_STATE_MANIFEST.json) · [`manifests/HALL_OF_TRIBUTE_MANIFEST.json`](manifests/HALL_OF_TRIBUTE_MANIFEST.json)

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
  ↓
0.8.5-D: bestätigte District-Folge ableiten
```

Wesentliche Garantien:

- vollständiger Settlement-Abschluss in **einem atomaren Persistence-Commit**
- Event ohne Krise ist gültig; fehlender Incident-State wird deterministisch als leer behandelt
- `pending_settlement` wird genau einmal verbraucht
- negatives Endbudget wird abgewiesen; kein erfundenes Schuldenmodell
- Stress bleibt `0..100`
- ältere Saves mit früher zulässigem negativem Ruf bleiben lesbar
- neue Settlement-Ergebnisse normalisieren Ruf auf mindestens `0`, damit Ranking kompatibel bleibt
- Budget-, Stress- und Ruf-Deltas im Receipt müssen exakt zu den bestätigten Effekten passen
- Biografieeintrag trägt die bestätigte Character-ID
- Heat/Stabilität bleiben bestätigte Settlement-Ergebnisse; 0.8.5-D leitet daraus erst nach bestätigtem Settlement die persistente District-Folge ab
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

## 🌆 0.8.5 – Living World & sichtbare Konkurrenz ✅

0.8.5 erweitert das erste Alpha **ohne versteckten Produktversionssprung** in fünf voneinander getrennten, jeweils remote validierten Schritten:

1. **Competitive Ranking:** aktuelle Metrik bleibt primär; bei Gleichstand gewinnt der steigende Challenger über bestätigtes Previous-Cycle-Momentum. Rangnummern bleiben eindeutig.
2. **Personalisierung:** Name, Alias, Spitznamen und Motto können im A4-Client bearbeitet werden; die technische Character-ID bleibt unveränderlich.
3. **Street Encounters:** stabile Walk-ID + deterministische Auswahl; kein Reload-Reroll und keine erfundenen Geld-/Itemgewinne.
4. **Living Districts:** bestätigte Street-/Settlement-Ergebnisse verändern die vier persistenten Bezirkswerte und bleiben replay-/recoveryfähig.
5. **Hall of Tribute:** dieselbe Ranking-Engine wird als read-only Top-10-Ansicht sichtbar; der Browser berechnet keine Rangfolge.

Der zunächst vorhandene PR #78 wurde **nicht** gemergt, weil er Living Districts unnötig mit Housing, Mehrstadtlogik, Trust und Minispielen gekoppelt hatte. PR #79 ersetzte ihn durch den kleineren District-Vertrag.

Der stärkste nächste Schritt ist deshalb **0.8.6-A Property Purchase Foundation**: Die City-Map besitzt bereits sieben kaufbare Orte und EconomyService die kanonische Geldautorität. Eigentum soll als eigener kleiner, replaybarer State hinzukommen – noch ohne Ausbau- oder Rendererlogik.

---

## 🧭 Einstieg ohne Vorwissen

1. Spielidee: [`docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md`](docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md)
2. **A4-First-Run Schritt für Schritt:** [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md)
3. allgemeiner Spieler-Einstieg: [`docs/SPIELERANLEITUNG.md`](docs/SPIELERANLEITUNG.md)
4. Entwicklergesamtbild: [`docs/SPIELBESCHREIBUNG_TECHNISCH.md`](docs/SPIELBESCHREIBUNG_TECHNISCH.md)
5. aktueller Entwicklungsblock: [`TODO.md`](TODO.md)
6. Ausbauvorrat: [`FEATURE_POOL.md`](FEATURE_POOL.md)

> [!NOTE]
> Der ältere HTML-Blueprint unter `web/` bleibt bewusst **schreibgeschützt und getrennt**. Der lokale A4-Game-Client befindet sich in `web/a4/` und schreibt ausschließlich über die Application-Grenze. District- und Hall-Daten werden read-only projiziert; ein hochwertiger Kartenrenderer und Property-Schreibpfad sind getrennte Folgeiterationen.

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
| Release-Nachweis | [`reports/RELEASE_0.8.4-alpha.1.json`](reports/RELEASE_0.8.4-alpha.1.json) |
| vollständige Spielidee ohne Technik | [`docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md`](docs/SPIELBESCHREIBUNG_OHNE_TECHNIK.md) |
| technische Gesamtbeschreibung | [`docs/SPIELBESCHREIBUNG_TECHNISCH.md`](docs/SPIELBESCHREIBUNG_TECHNISCH.md) |
| A4 First Run | [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md) |
| A4 Schreibgrenze | [`docs/A4_WRITING_CLIENT_0.8.4.md`](docs/A4_WRITING_CLIENT_0.8.4.md) |
| Spieler-Einstieg | [`docs/SPIELERANLEITUNG.md`](docs/SPIELERANLEITUNG.md) |
| aktuellen Entwicklungsstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| nächste Aufgaben | [`TODO.md`](TODO.md) |
| Feature-Pool | [`FEATURE_POOL.md`](FEATURE_POOL.md) |
| Event State | [`docs/EVENT_STATE_0.8.1.md`](docs/EVENT_STATE_0.8.1.md) |
| Event Actions | [`manifests/EVENT_ACTION_MANIFEST.json`](manifests/EVENT_ACTION_MANIFEST.json) |
| Crisis + Berlin Map | [`docs/CRISIS_CITY_0.8.3-B.md`](docs/CRISIS_CITY_0.8.3-B.md) |
| Incident-Katalog | [`manifests/INCIDENT_MANIFEST.json`](manifests/INCIDENT_MANIFEST.json) |
| Settlement | [`docs/SETTLEMENT_0.8.3-C.md`](docs/SETTLEMENT_0.8.3-C.md) · [`manifests/SETTLEMENT_MANIFEST.json`](manifests/SETTLEMENT_MANIFEST.json) |
| Living Districts | [`manifests/DISTRICT_STATE_MANIFEST.json`](manifests/DISTRICT_STATE_MANIFEST.json) · [`schemas/district_state.schema.json`](schemas/district_state.schema.json) |
| Hall of Tribute | [`manifests/HALL_OF_TRIBUTE_MANIFEST.json`](manifests/HALL_OF_TRIBUTE_MANIFEST.json) |
| Competitive Ranking | [`manifests/RANKING_NETWORK_MANIFEST.json`](manifests/RANKING_NETWORK_MANIFEST.json) |
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
Domain: CharacterState + EventState + EconomyState + IncidentState + SettlementState + DistrictState
  ↓
Application: Character / Street / Event / Economy / Execution / Incident / Settlement / District Services
  ↑                     ↓
  └──── GameClientSession (nur Routing/Orchestrierung, keine zweite Fachlogik)
                        ↓
Persistence: Journal + State + Snapshot + Recovery
                        ↓
Read-only Projections
  ├─→ Character / Feedback
  ├─→ Competitive Ranking / Hall of Tribute
  ├─→ Living Districts / Berlin Ops Map
  └─→ A4 Game Projection
                        ↓
A4 Game Client / A3 / spätere Kartenansicht
```

| Bereich | Verantwortung | Grenze |
|---|---|---|
| `domain` | Charakter, Progression, Event, Economy, Incident, Settlement, District | kennt keine UI/Infrastruktur |
| `application` | Use Cases, Commands, atomare Orchestrierung, GameClientSession-Routing | umgeht Persistenz nicht; dupliziert keine Domainregeln |
| `infrastructure` | Journal, Save, Snapshot, Recovery | verwaltet keine sichtbaren UI-Texte |
| `presentation` | Projection, Komponenten, Hall/Map-Darstellung | schreibt Domain-/Save-State nicht direkt |
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

### Release Package

```bash
PYTHONPATH=src:. python3 -m unittest tests.runtime.test_release_package -v
python3 tools/build_release.py --output-dir dist
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
- 0.8.4-alpha.1 Release / PR #73: Runtime Core `32576855723`, Presentation Core `32576855749`, Repository Health `32576855738`, Release Acceptance `32576855720`, Release Package `32576855768`; 0 ungelöste Review-Threads; `SAFE MERGE PASS`; Merge `3fdb5cc3d57e73734d1f594603cafdd6d06c5210`
- 0.8.5-A / PR #75: Runtime Core `32578257295`, Presentation Core `32578257274`, Repository Health `32578257380`, Release Acceptance `32578257240`, Release Package `32578257345`; Merge `b41d8f416679515307f2a580fb66b0569057836a`
- 0.8.5-B / PR #76: Runtime Core `32578559486`, Presentation Core `32578559454`, Repository Health `32578559549`, Release Acceptance `32578559453`, Release Package `32578559471`; Merge `5a9eed536d48f30cdd1f4569e9e1b1724e5ced80`
- 0.8.5-C / PR #77: Runtime Core `32579029076`, Presentation Core `32579028963`, Repository Health `32579028895`, Release Acceptance `32579028891`, Release Package `32579028890`; Merge `38de9f42c2908d63945db7bf25277b2f940ede6e`
- 0.8.5-D / PR #79: Runtime Core `32586077024`, Presentation Core `32586077030`, Repository Health `32586077045`, Release Acceptance `32586077027`, Release Package `32586077025`; 0 Review-Threads; Merge `98c8b84715cc308dd1bc9fd92b7c7e56a35cc861`
- 0.8.5-E / PR #80: Runtime Core `32586394504`, Presentation Core `32586394533`, Repository Health `32586394437`, Release Acceptance `32586394507`, Release Package `32586394495`; 0 Review-Threads; Merge `d383a3f364c6ee8cd954041f1d324e0ace0cb357`

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
- [`reports/RELEASE_0.8.4-alpha.1.json`](reports/RELEASE_0.8.4-alpha.1.json)
- [`manifests/CITY_MAP_MANIFEST.json`](manifests/CITY_MAP_MANIFEST.json)
- [`manifests/DISTRICT_STATE_MANIFEST.json`](manifests/DISTRICT_STATE_MANIFEST.json)
- [`schemas/district_state.schema.json`](schemas/district_state.schema.json)
- [`manifests/RANKING_NETWORK_MANIFEST.json`](manifests/RANKING_NETWORK_MANIFEST.json)
- [`manifests/HALL_OF_TRIBUTE_MANIFEST.json`](manifests/HALL_OF_TRIBUTE_MANIFEST.json)
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
