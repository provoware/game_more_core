<div align="center">

# BUNKERFREQUENZ

### Beton. Bass. Berlin.

**Techno-/FreeTekno-Crew-RPG · Character Forge · Event-Management · Living Districts · Property Progression**

<p>
  <img alt="Runtime Baseline 0.8.4 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.8.4--alpha.1-ff4d00">
  <img alt="Feature Stand 0.8.7 C5 validiert" src="https://img.shields.io/badge/Feature_Stand-0.8.7--C5_validiert-7dff00">
  <img alt="Timeline sichtbar" src="https://img.shields.io/badge/Timeline-C4B_sichtbar-00c2ff">
  <img alt="District Cadence validiert" src="https://img.shields.io/badge/District_Cadence-C5_validiert-ff7ad9">
  <img alt="Mergeweg Safe Merge" src="https://img.shields.io/badge/Mergeweg-%2Fsafe--merge-8a2be2">
</p>

> **Entdecken → entscheiden → planen → handeln → eskalieren → abrechnen → Stadt verändern → Orte übernehmen → ausbauen → aufsteigen.**

</div>

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

---

## ⚡ Projekt-Puls

| | Aktueller Stand |
|---|---|
| **Release-Baseline** | `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease |
| **Validierter Feature-Stand** | ✅ `0.8.7-C5 – District-Event Cadence/Cooldown` |
| **Aktive Iteration** | 🟡 `0.8.8-A – Crew Identity Foundation` |
| **Lokaler Game Client** | ✅ schreibender A4-Client, localhost-only |
| **Living World** | ✅ replaybare Street Encounters, persistente Districts, District World Events + 24h-Cadence |
| **Timeline** | ✅ Street-, Krisen- und District-Ereignisse read-only im Control Deck sichtbar |
| **Ranking** | ✅ Competitive Top 10 + bestätigte Wochen-/Monatszyklen |
| **Property** | ✅ 7 kaufbare Orte + 10 Ausbauarten, Level 1–3 |
| **Berlin Ops Map PRO** | ✅ 8 Districts · 12 Locations · read-only |
| **Control Deck 2.0** | ✅ HUD, Schnellnavigation und lokale Anzeigeoptionen |
| **Netzwerk/Telegram** | noch nicht implementiert; keine erfundenen Remote-Spieler |

> [!IMPORTANT]
> `0.8.7-C5` ist remote validiert und ausschließlich über `/safe-merge` nach `main` gelangt. Die Produktversion bleibt bewusst `0.8.4-alpha.1`. Feature-Fortschritt ist kein stiller Release.

---

## 🎮 Spielkern

BUNKERFREQUENZ ist ein lokales Techno-/FreeTekno-Crew-RPG. Bestätigte Aktionen, Ereignisse und ihre Folgen formen Charakter, Crew und Stadt.

```text
STRASSE / SPIELERANSATZ
      ↓
CHARAKTER & CREW
      ↓
EVENT PLANEN
      ↓
EQUIPMENT / PROPERTY / STADTLAGE
      ↓
EVENT STARTEN
      ↓
KRISE? → FOLGEN ANSEHEN → ENTSCHEIDEN
      ↓
SETTLEMENT
      ↓
DISTRICT WORLD EVENT (CADENCE-GEFÜHRT)
      ↓
RUF · SKILLS · BIOGRAFIE · TIMELINE
      ↓
LIVING DISTRICTS / BERLIN OPS MAP
      ↓
PROPERTY / HALL OF TRIBUTE
```

### Bereits validiert

- 16 Skills, 165 Trait-Namen, Level 1–50 + Resonanz
- Event-State, Equipment/Economy, Krisen und Settlement
- Save, Snapshot, Restart und Recovery
- Street Encounters ohne Reload-Reroll
- persistente District-Werte
- Property Purchase + dreistufige Upgrades
- Berlin Ops Map PRO
- Competitive Top 10 + Wochen-/Monatszyklen
- Control Deck 2.0 mit Street Approaches und Krisen-Folgenvorschau
- sichtbare read-only Ereignis-Timeline
- District World Events mit deterministischer Auswahl und 24h-Cadence aus bestätigter Spielweltzeit

---

## 🌆 0.8.7-C – District World Events & Timeline ✅

### C1–C3: Vertrag, Runtime, Application

Vier erste Bezirksereignisse verwenden stabile IDs, katalogisierte Voraussetzungen und kleine District-Effekte. Die Auswahl bleibt deterministisch aus `world_seed + district_id + trigger_id`. Der Browser kann weder Ereignisse aktivieren noch Gewichte oder Effekte einspeisen. `settlement.complete` ist der einzige autorisierte Application-Trigger.

### C4A/C4B: Ereignis-Timeline

Die Timeline liest ausschließlich bestätigte Journalrecords für Street Encounters, gelöste Krisen und District-Ereignisse. C4A liefert die kanonische Projection; C4B zeigt sie im Control Deck an. Der Browser übernimmt Reihenfolge und Texte read-only und besitzt keinen zweiten Story- oder Save-Pfad.

**Remote-Abnahme C4B:** PR #101 · Head `e23271c5dcb1463d68178b37faa2602d24d6eb46` · 5/5 Gates · SAFE MERGE PASS · Merge `3d71f00c5717ae797e6b8f1ca4c65c036bf71c81`.

### C5: Cadence/Cooldown

District-Ereignisse werden global über **24 Stunden bestätigte Spielweltzeit** dosiert. Autorität ist `event.time_window.start_local`; Systemzeit ist kein Fallback. Ein Trigger innerhalb des Cooldowns bleibt ein schreibfreier No-op. Retry und Reload würfeln bestätigte Trigger nicht neu.

**Remote-Abnahme C5:** PR #102 · Head `05eef417efa24f299ebc7de7f2104f6a625d5582` · Runtime `32646269065` · Presentation `32646269053` · Repository Health `32646269009` · Release Acceptance `32646269064` · Release Package `32646269010` · SAFE MERGE PASS · Merge `bd79da8d1e124ec60248a05bf332c6ef338ca7b6`.

---

## 🧭 0.8.8 – geplanter Ausbau

Der nächste Ausbau wird bewusst in getrennte, prüfbare Slices zerlegt:

| Slice | Ziel | Kernregel |
|---|---|---|
| **0.8.8-A** | Crew-Logo/Fahne | synchronisierbare Identitätsdaten statt Bildblob |
| **0.8.8-B** | Scene Jobs | jederzeit nutzbare, katalogisierte Geld-/Ressourcenaktionen |
| **0.8.8-C** | Secret Best Friend Assistant | genau eine wiederholte Aufgabe bis Deaktivierung |
| **0.8.8-D** | Bank & Investments | journalisierte Ein-/Auszahlungen, Zins, Zinseszins, Anlagen, Dividenden, Auszüge |
| **0.8.8-E** | Control Deck Focus | weniger doppelte Ansichten, lokale Bereichsmaximierung, klare nächste Aktionen |
| **0.8.8-F** | Berlin Ops Map 2 | bezirksartige Zoom-/Pan-Ansicht mit besserer Objekt-Hierarchie |

Story-Nachhall und lokaler Timeline-Fokusfilter bleiben eigenständige Folge-Slices, damit Story, Economy, UI und Sync nicht in einer Mega-Änderung vermischt werden.

---

## 🗺️ Berlin Ops Map PRO ✅

Die aktuelle Karte bleibt eine reine Presentation-Schicht:

- 8 District-Flächen und 12 Locations
- Heat, Prestige, Polizeidruck, Szeneaktivität
- Score/Tier/Rang
- Eigentum + Ausbau
- Hall-Markierung
- Filter `all / owned / prime / hall`
- Tastaturfokus + ARIA + Reduced Motion

`map_pro.js` besitzt keine eigene Domainlogik, kein `/api/command`, kein Geocoding und keinen externen Kartendienst. Die geplante Map 2 darf diese Grenze nicht aufbrechen.

---

## 🚀 Start für absolute Anfänger

Im Projektordner:

```bash
./START_BUNKERFREQUENZ.sh
```

Bei belegtem Port:

```bash
./START_BUNKERFREQUENZ.sh --port 0
```

Alternativ:

```bash
python3 tools/start_a4_game_client.py
```

Der Server bindet ausschließlich an `127.0.0.1`.

Ausführliche Erklärung: [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md)

---

## 🧱 Architekturgrenzen

```text
DOMAIN
  ↓
APPLICATION SERVICES
  ↓
PERSISTENCE / JOURNAL / RECOVERY
  ↓
READ-ONLY PROJECTIONS
  ↓
A4 CONTROL DECK
```

| Ebene | Darf | Darf nicht |
|---|---|---|
| Domain | Invarianten/Zustandsregeln | UI kennen |
| Application | Use Cases und Orchestrierung | Persistenz umgehen |
| Infrastructure | Journal/State/Snapshot/Recovery | Gameplay erfinden |
| Presentation | bestätigte Daten erklären/darstellen | Domain-/Save-State direkt schreiben |
| Browser-UI | Auswahl-IDs und lokale Darstellung senden | Preise, Erträge, Effekte, Zinsen oder Regeln autorisieren |

Neue UI-Funktionen wie Zoom, Filter, Fokus-Maximierung oder Aktionshervorhebung bleiben lokale Presentation. Wiederholte Assistentenaktionen, Zinsen und Dividenden benötigen bestätigte Spielautorität und dürfen nicht durch die Rechneruhr allein fortschreiten.

---

## 🛡️ Persistenz & Recovery

- append-only JSONL-Journal
- SHA-256-Hashkette
- atomare State-/Meta-Writes
- Snapshots
- Replay/Recovery aus bestätigtem Journal
- Quarantäne beschädigter Journal-Tails
- Fault-Injection-Regressionen

> **Ein UI-Refresh, Zoom, Filter oder andere Anzeigeeinstellung darf niemals Gameplay erneut würfeln oder bestätigte Fachwerte verändern.**

---

## ✅ Wichtige Meilensteine

| Iteration | Kern | Merge |
|---|---|---|
| 0.8.4-alpha.1 | erster freigegebener lokaler Release | `3fdb5cc3d57e...` |
| 0.8.5-C | replaybare Street Encounters | `38de9f42c290...` |
| 0.8.5-D | Living Districts | `98c8b84715cc...` |
| 0.8.5-E | Hall of Tribute | `d383a3f364c6...` |
| 0.8.6-A | Property Purchase | `192b3eb4ad9d...` |
| 0.8.6-B | Property Upgrades | `0b301bc9004f...` |
| 0.8.6-C | Berlin Ops Map PRO | `10c7d6b5e048...` |
| 0.8.7-A | Saisonale Hall of Tribute | `841258a37915...` |
| 0.8.7-B | Control Deck & Player Choices | `4d1a35bfbc08...` |
| 0.8.7-C4B | sichtbare Ereignis-Timeline | `3d71f00c5717...` |
| **0.8.7-C5** | **District-Event Cadence/Cooldown** | `bd79da8d1e12...` |

---

## 📦 Release-Baseline

```text
BUNKERFREQUENZ-0.8.4-alpha.1.zip
SHA-256:
fccf16ee3728827ba4eba0dfd0e3cbaf844dd68c382b3c29c766f94a7ef85146
```

Feature-Fortschritt auf `main` ist kein stiller Produktrelease. Eine neue Produktversion braucht eine eigene Release-Iteration.

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
Release Acceptance ✅
Release Package ✅
        ↓
0 Review-Threads
        ↓
/safe-merge
        ↓
SAFE MERGE PASS
```

---

## 🗂️ Schnellzugriff

| Gesucht | Datei |
|---|---|
| Maschinenstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| aktive Arbeit | [`TODO.md`](TODO.md) |
| Ausbauvorrat | [`FEATURE_POOL.md`](FEATURE_POOL.md) |
| Projektmanifest | [`PROJEKTMANIFEST.json`](PROJEKTMANIFEST.json) |
| Anfängerstart | [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md) |
| District-Event-Vertrag | [`manifests/DISTRICT_EVENT_MANIFEST.json`](manifests/DISTRICT_EVENT_MANIFEST.json) |
| Berlin Ops Map | [`manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json`](manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json) |
| Safe Merge | [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md) |

---

## 🔧 Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Keine zweite Architektur, keine Browser-Fachlogik und keine stillen Versionssprünge. Normale PRs nach `main` werden ausschließlich über `/safe-merge` übernommen.

Details: [`AGENTS.md`](AGENTS.md) · [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) · [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md)
