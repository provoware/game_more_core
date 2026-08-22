<div align="center">

# BUNKERFREQUENZ

### Beton. Bass. Berlin.

**Techno-/FreeTekno-Crew-RPG · Character Forge · Event-Management · Living Districts · Property Progression**

<p>
  <img alt="Runtime Baseline 0.8.4 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.8.4--alpha.1-ff4d00">
  <img alt="Feature Stand 0.8.6 C validiert" src="https://img.shields.io/badge/Feature_Stand-0.8.6--C_validiert-7dff00">
  <img alt="Property Purchase validiert" src="https://img.shields.io/badge/Property_Purchase-0.8.6--A_validiert-f2c744">
  <img alt="Property Upgrades validiert" src="https://img.shields.io/badge/Property_Upgrades-0.8.6--B_validiert-e840ff">
  <img alt="Berlin Ops Map PRO validiert" src="https://img.shields.io/badge/Berlin_Ops_Map_PRO-0.8.6--C_validiert-00c2ff">
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
| **Validierter Feature-Stand** | ✅ `0.8.6-C` |
| **Lokaler Game Client** | ✅ schreibender A4-Client, localhost-only |
| **Event-Loop** | ✅ Planung → Beschaffung → Aufbau → Live → Krise optional → Abbau → Settlement → completed |
| **Living World** | ✅ Street Encounters + persistente District-Metriken |
| **Ranking** | ✅ Competitive Top 10 + Hall of Tribute |
| **Immobilien** | ✅ 7 kaufbare Orte, bestätigtes Eigentum |
| **Ausbau** | ✅ 10 Ausbauarten, Level 1–3, atomare Kostenbuchung, Kartenwirkung |
| **Berlin Ops Map PRO** | ✅ 8 Districts · 12 Locations · Eigentum/Ausbau · vier Sichtfilter · read-only |
| **Recovery** | ✅ Combined Replay für Character, Event, Economy, Incident, Settlement, District, Property und PropertyUpgrade |
| **Nächster Block** | `0.8.7-A – Saisonale Hall of Tribute` |
| **Netzwerk/Telegram** | noch nicht implementiert; keine erfundenen Remote-Spieler |

> [!IMPORTANT]
> `0.8.6-C` ist **validierter Feature-Fortschritt**, kein stiller Produktrelease. Die veröffentlichte Runtime-Baseline bleibt `0.8.4-alpha.1`, bis eine neue eigene Release-Abnahme durchgeführt wird.

---

## 🎮 Was ist BUNKERFREQUENZ?

BUNKERFREQUENZ ist ein lokales Techno-/FreeTekno-Crew-RPG. Nicht eine starre Klasse, sondern bestätigtes Verhalten formt Charakter, Crew und Stadt.

```text
STRASSE / ENTDECKEN
      ↓
CHARAKTER & CREW ENTWICKELN
      ↓
EVENT PLANEN UND VORBEREITEN
      ↓
EVENT / KRISE / ENTSCHEIDUNG
      ↓
SETTLEMENT
      ↓
RUF · SKILLS · TRAITS · BIOGRAFIE
      ↓
LIVING DISTRICTS
      ↓
IMMOBILIEN ÜBERNEHMEN UND AUSBAUEN
      ↓
BERLIN OPS MAP PRO
      ↓
HALL OF TRIBUTE / LANGZEITPROGRESSION
```

### Character Forge

- **16 Skills** statt fester Klassen
- **165 Trait-Namen** auf kontrollierten Effektfamilien
- Level 1–50, danach offene Resonanzränge
- Energie und Stress `0..100`
- Profilname, Alias, Spitznamen und Motto editierbar
- Biografie ausschließlich aus bestätigten Journal-Ereignissen

### Living World

- 8 stilisierte Berliner Bezirke
- 12 katalogisierte Spielorte
- persistente Bezirkswerte `heat`, `prestige`, `police_pressure`, `scene_activity`
- deterministische Street Encounters ohne Reload-Reroll
- Hall of Tribute mit bestätigtem Ranking
- 7 kaufbare Properties und 10 Ausbauarten

---

## 🏢 0.8.6-A/B – Property Progression ✅

### Immobilien kaufen

Der Client sendet nur die `location_id`. Preis, Eigentümer und Budgetdelta stammen aus der Runtime.

```text
A4
 ↓ property.purchase(location_id)
GameClientSession
 ↓
PropertyService + EconomyService
 ↓
EIN atomarer Persistence-Commit
 ├─ economy.transaction_posted
 └─ world.property_purchased
 ↓
Economy + Event-Budget + PropertyState
```

Garantien:

- Kaufpreis ausschließlich aus `CITY_MAP_MANIFEST`
- keine Client-Preisautorität
- nicht kaufbare Orte und Doppelkäufe fail-closed
- kein Zwischenzustand „Geld weg, Eigentum fehlt“
- Combined Recovery rekonstruiert Geld und Eigentum gemeinsam

**0.8.6-A:** PR #82 · Merge `192b3eb4ad9dc4272eafeddc8604f7265bdd30fa`.

### Immobilien ausbauen

Ausbau besitzt einen separaten `PropertyUpgradeState`. Der Browser sendet nur `location_id + upgrade_id`.

- 10 Ausbauarten
- maximales Level **3**
- Kostenmultiplikatoren **1,00× / 1,50× / 2,25×**
- Kostenbasis: bestätigter ursprünglicher Immobilienkaufpreis
- keine Client-Autorität über Kosten, Level, Wertdelta oder Menge
- Economy + Event-Budget + Upgrade-State atomar
- `world.property_upgraded` replaybar
- Combined Recovery einschließlich Fault nach durablem Journal
- effektive Werte bleiben `0..100`
- vorhandene `city_map_projection` bleibt einzige Score-/Tier-Autorität

**0.8.6-B:** PR #83 · Head `acbf6b1c5615137664ed4ad84fb0535bea297030` · 5/5 Gates · Merge `0b301bc9004f60dbc3ce221a7c6b3e462766b5b7`.

---

## 🗺️ 0.8.6-C – Berlin Ops Map PRO ✅

Die Karte ist jetzt eine echte, hochwertige **read-only Handlungsebene** auf bereits bestätigten Daten.

```text
bestätigter State
      ↓
Living District / City Map / Property / Upgrade Projections
      ↓
BerlinOpsMapPro Projection
      ↓
map_pro.js – reine Darstellung
```

### Sichtbar auf der Karte

- **8 District-Flächen** mit Heat, Prestige, Polizeidruck und Szeneaktivität
- **12 Locations** mit Score, Tier und Rang
- Eigentumsmarkierung
- bestätigte Ausbaulevel
- fünf effektive Standortwerte
- Hall of Tribute als besonderer Marker
- Detailpanel bei Fokus oder Klick

### Vier reine Sichtfilter

1. Alle Orte
2. Mein Eigentum
3. Prime + Legendary
4. Hall of Tribute

Filter verändern **keinen Spielzustand**.

### Harte Sicherheitsgrenze

`web/a4/map_pro.js` besitzt absichtlich:

- kein `/api/command`
- kein eigenes `fetch()`
- keine Domain-/Save-Writes
- kein `localStorage`/`sessionStorage` als Autorität
- keine Geolocation
- kein Google Maps, Mapbox oder Leaflet
- kein Geocoding
- keine Navigationslogik

Score, Tier, Eigentum und Ausbau werden nicht im Renderer berechnet, sondern ausschließlich aus bestätigten Projections übernommen.

### Bedienbarkeit

- Tastaturfokus
- sichtbarer Fokus
- ARIA-Beschriftungen
- Information nicht nur über Farbe: Tierformen, Eigentumsring und Hall-Form
- Reduced-Motion-Fallback
- responsive Desktop-/Tablet-/Mobilansicht

### Remote-Abnahme 0.8.6-C

- PR #85
- Head `6c302ce9425b27e7a1175a1cdcf463a100fc7191`
- Runtime Core `32592128107` ✅
- Presentation Core `32592128117` ✅
- Repository Health `32592128103` ✅
- Release Acceptance `32592128147` ✅
- Release Package `32592128113` ✅
- Review-Threads: `0`
- `/safe-merge`: **PASS**
- Merge `10c7d6b5e04838b07ae6899b8b76580cd87de607`

Vertrag: [`manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json`](manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json) · Projection: [`src/bunkerfrequenz/presentation/berlin_ops_map_pro.py`](src/bunkerfrequenz/presentation/berlin_ops_map_pro.py) · Renderer: [`web/a4/map_pro.js`](web/a4/map_pro.js)

---

## 🏆 Nächster Schritt: 0.8.7-A – Saisonale Hall of Tribute

Die Hall, Competitive-Ranking-Engine und Bewegungsanzeige sind stabil. Der nächste Ausbau ergänzt bestätigte **Wochen-/Monatszyklen** und Prestige-Titel.

Harte Vorgaben:

- Systemzeit ist niemals alleinige Zyklusautorität.
- Wiederholung desselben bestätigten Zyklus bleibt deterministisch.
- Die bestehende Ranking-Engine wird wiederverwendet.
- Lokale Hall-Daten erfinden weiterhin keine Gegner.
- Titel entstehen nur aus bestätigtem Zyklus + bestätigtem Ranking.

Vorgemerkte Titel: **Lärmadel, Bunkerbaron, Kabelkönig, Pegelpapst, Stromheiland, Betonlegende, Nachtminister**.

Aktiver Plan: [`TODO.md`](TODO.md)

---

## 🚀 Start für absolute Anfänger

Im Projektordner:

```bash
./START_BUNKERFREQUENZ.sh
```

Automatische freie Portwahl:

```bash
./START_BUNKERFREQUENZ.sh --port 0
```

Alternativ:

```bash
python3 tools/start_a4_game_client.py
```

Der lokale Server bindet ausschließlich an `127.0.0.1`. Vorhandene Saves werden nicht still überschrieben.

Jeder bestätigte Command wird unmittelbar journalisiert; zusätzlich kann ein manueller Snapshot/Checkpoint erzeugt werden.

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
├─ Character / Profile / Street
├─ Event / Economy / Incident / Settlement
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
└─ Berlin Ops Map PRO
        ↓
A4 GAME CLIENT
```

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

Combined Recovery kennt:

```text
Character → Event → Economy → Incident → Settlement → District → Property → PropertyUpgrade
```

> **Geld und Eigentum/Ausbau dürfen nach einem Crash niemals auf unterschiedlichen bestätigten Ständen verbleiben.**

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
| 0.8.6-A | Property Purchase | `192b3eb4ad9d...` |
| 0.8.6-B | Property Upgrades | `0b301bc9004f...` |
| **0.8.6-C** | **Berlin Ops Map PRO** | `10c7d6b5e048...` |

---

## 📦 Release-Baseline

```text
BUNKERFREQUENZ-0.8.4-alpha.1.zip
SHA-256:
fccf16ee3728827ba4eba0dfd0e3cbaf844dd68c382b3c29c766f94a7ef85146
```

0.8.5 und 0.8.6 sind danach validierte Feature-Entwicklung auf `main`. Eine neue Produktversion wird erst nach einer eigenen Release-Iteration festgelegt.

---

## 🧪 Qualitäts-Gates

```bash
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
PYTHONPATH=src:. python3 -m unittest discover -s tests/repository -v
PYTHONPATH=src python3 tools/repository_health.py
```

Normaler Mergepfad:

```text
aktueller main enthalten
        ↓
Runtime Core ✅
Presentation Core ✅
Repository Health ✅
Release Acceptance / Package ✅
        ↓
0 Review-Threads
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
| City Map | [`manifests/CITY_MAP_MANIFEST.json`](manifests/CITY_MAP_MANIFEST.json) |
| Berlin Ops Map PRO | [`manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json`](manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json) |
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
