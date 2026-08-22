<div align="center">

# BUNKERFREQUENZ

### Beton. Bass. Berlin.

**Techno-/FreeTekno-Crew-RPG · Character Forge · Event-Management · Living Districts · Property Progression**

<p>
  <img alt="Runtime Baseline 0.8.4 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.8.4--alpha.1-ff4d00">
  <img alt="Feature Stand 0.8.7 A validiert" src="https://img.shields.io/badge/Feature_Stand-0.8.7--A_validiert-7dff00">
  <img alt="Berlin Ops Map PRO validiert" src="https://img.shields.io/badge/Berlin_Ops_Map_PRO-validiert-00c2ff">
  <img alt="Seasonal Hall validiert" src="https://img.shields.io/badge/Seasonal_Hall-0.8.7--A_validiert-ff7ad9">
  <img alt="Control Deck in validation" src="https://img.shields.io/badge/Control_Deck-0.8.7--B_in_Abnahme-f2c744">
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
| **Validierter Feature-Stand** | ✅ `0.8.7-A – Saisonale Hall of Tribute` |
| **Aktive Iteration** | 🟡 `0.8.7-B – Control Deck & Player Choices` – noch nicht remote abgenommen |
| **Lokaler Game Client** | ✅ schreibender A4-Client, localhost-only |
| **Living World** | ✅ replaybare Street Encounters + persistente District-Metriken |
| **Ranking** | ✅ Competitive Top 10 + bestätigte Wochen-/Monatszyklen |
| **Property** | ✅ 7 kaufbare Orte + 10 Ausbauarten, Level 1–3 |
| **Berlin Ops Map PRO** | ✅ 8 Districts · 12 Locations · read-only |
| **Control Deck 2.0** | 🟡 HUD, Schnellnavigation und lokale Anzeigeoptionen im 0.8.7-B-Kandidaten |
| **Spielerentscheidungen** | 🟡 Street Approaches + Krisen-Folgenvorschau im 0.8.7-B-Kandidaten |
| **Recovery** | ✅ Combined Replay für persistente Kernblöcke |
| **Netzwerk/Telegram** | nicht implementiert; keine erfundenen Remote-Spieler |

> [!IMPORTANT]
> `0.8.7-A` ist remote validiert und sicher gemergt. `0.8.7-B` ist **aktive Feature-Entwicklung** und wird erst nach grünen Gates + `/safe-merge` als validiert bezeichnet. Die Produktversion bleibt `0.8.4-alpha.1`.

---

## 🎮 Was ist BUNKERFREQUENZ?

BUNKERFREQUENZ ist ein lokales Techno-/FreeTekno-Crew-RPG. Entscheidungen, bestätigte Aktionen und ihr Verlauf formen Charakter und Stadt.

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
RUF · SKILLS · BIOGRAFIE
      ↓
LIVING DISTRICTS / BERLIN OPS MAP
      ↓
PROPERTY / AUSBAU
      ↓
HALL OF TRIBUTE / SAISON
```

### Bereits validiert

- 16 Skills, 165 Trait-Namen, Level 1–50 + Resonanz
- Event-State, Equipment/Economy, Krisen und Settlement
- Save, Snapshot, Restart und Recovery
- Street Encounters ohne Reload-Reroll
- persistente District-Werte
- Property Purchase + dreistufige Upgrades
- Berlin Ops Map PRO
- Competitive Top 10
- Wochen-/Monatszyklen der Hall of Tribute

---

## 🏆 0.8.7-A – Saisonale Hall of Tribute ✅

Die Hall verwendet weiterhin dieselbe Competitive-Ranking-Engine. Neu sind bestätigte Wochen-/Monatszyklen und Titelprojektionen.

### Sicherheitsregeln

- Systemzeit ist **niemals** alleinige Saisonautorität.
- Ein abgeschlossenes bestätigtes Event kann einen stabilen lokalen `game_world_time`-Anker liefern.
- Endgültige Titel brauchen einen bestätigten geschlossenen Zyklus.
- Ein endgültiger Championtitel braucht echte bestätigte Konkurrenz.
- Ein lokaler Einzelspieler-Rang 1 erzeugt keinen Fake-Champion.
- Kein zweites Ranking-System wurde eingeführt.

**Remote-Abnahme:** PR #87 · Head `b887f912675ed2cf5efa8eb85631ab7858721836` · 5/5 Gates · SAFE MERGE PASS · Merge `841258a37915e05d7f87eed7841c8e4b8d79bf46`.

---

## 🎛️ 0.8.7-B – Control Deck & Player Choices 🟡

Dieser Slice verbessert Optik, Bedienung und echte Auswahlmöglichkeiten. Er ist im aktuellen Featurebranch implementiert, aber noch nicht als validiert markiert.

### Control Deck 2.0

- sticky HUD für Phase, Budget, Energie, Stress, Ruf und Eigentum
- Schnellnavigation zu Straße, Map, Property, Hall, Event, Equipment und Save
- stärkere Industrial-Control-Room-Hierarchie
- responsive Desktop-/Tablet-/Mobilansicht
- Entscheidungselemente werden deutlicher als reine Statusflächen dargestellt

### Lokale Anzeigeoptionen

Im Browser können drei reine Darstellungsoptionen gewählt werden:

- **Kompakt** – weniger Abstand, mehr Informationen gleichzeitig
- **Hoher Kontrast** – stärkere Linien und Statusflächen
- **Große Schrift** – bessere Lesbarkeit

Diese Einstellungen werden nur lokal im Browser gespeichert. Sie besitzen **keine** Domain-, Save-, Economy- oder Ranking-Autorität.

### Street Approaches

Vor einer Straßenrunde kann der Spieler einen Ansatz wählen:

| Ansatz | Idee |
|---|---|
| **Ausgeglichen** | exakt die bisherige Encounter-Verteilung |
| **Runterkommen** | mehr Ruhe, Wasser, Kaffee und Erholung |
| **Kontakte** | stärker auf bekannte Gesichter/Crews ausgerichtet |
| **Scout** | mehr Wege/Funde, aber etwas mehr Ärger möglich |

Der Ansatz verändert **nur katalogisierte Auswahlgewichte**. Der Encounter selbst bleibt die einzige Effekt-Autorität. Der Browser sendet nur `approach_id`; Gewichte oder Effekte können nicht eingespeist werden.

Alte `0.8.5-c1`-Street-Records bleiben replaybar und werden als `balanced` interpretiert.

### Krisenentscheidungen

Die vorhandene Crisis Engine bleibt unverändert zuständig. Das Control Deck zeigt vor der Antwort lediglich die bereits katalogisierten Auswirkungen, z. B.:

- Budget
- Ruf
- Crew-Stress
- Stabilität
- Heat
- Zielphase

Der Browser sendet weiterhin nur die bestehende `response_id`.

---

## 🗺️ Berlin Ops Map PRO ✅

Die Karte bleibt eine reine Presentation-Schicht:

- 8 District-Flächen
- 12 Locations
- Heat, Prestige, Polizeidruck, Szeneaktivität
- Score/Tier/Rang
- Eigentum + Ausbau
- Hall-Markierung
- Filter `all / owned / prime / hall`
- Tastaturfokus + ARIA + Reduced Motion

`map_pro.js` besitzt keine eigene Domainlogik, kein `/api/command`, kein Geocoding und keinen externen Kartendienst.

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
| Browser-UI | Auswahl-IDs senden, lokale Darstellung | Preise, Effekte, Gewichte oder Regeln autorisieren |

---

## 🛡️ Persistenz & Recovery

- append-only JSONL-Journal
- SHA-256-Hashkette
- atomare State-/Meta-Writes
- Snapshots
- Replay/Recovery aus bestätigtem Journal
- Quarantäne beschädigter Journal-Tails
- Fault-Injection-Regressionen

> **Ein UI-Refresh oder eine andere Anzeigeeinstellung darf niemals Gameplay erneut würfeln oder bestätigte Fachwerte verändern.**

---

## ✅ Wichtige Meilensteine

| Iteration | Kern | Merge |
|---|---|---|
| 0.8.4 | schreibender A4 Game Client | `28459c197489...` |
| 0.8.4-alpha.1 | erster freigegebener lokaler Release | `3fdb5cc3d57e...` |
| 0.8.5-C | replaybare Street Encounters | `38de9f42c290...` |
| 0.8.5-D | Living Districts | `98c8b84715cc...` |
| 0.8.5-E | Hall of Tribute | `d383a3f364c6...` |
| 0.8.6-A | Property Purchase | `192b3eb4ad9d...` |
| 0.8.6-B | Property Upgrades | `0b301bc9004f...` |
| 0.8.6-C | Berlin Ops Map PRO | `10c7d6b5e048...` |
| **0.8.7-A** | **Saisonale Hall of Tribute** | `841258a37915...` |
| **0.8.7-B** | **Control Deck & Player Choices** | *in Abnahme* |

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
| Street-Vertrag | [`manifests/STREET_ENCOUNTER_MANIFEST.json`](manifests/STREET_ENCOUNTER_MANIFEST.json) |
| Hall-Saison | [`manifests/HALL_SEASON_MANIFEST.json`](manifests/HALL_SEASON_MANIFEST.json) |
| Berlin Ops Map | [`manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json`](manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json) |
| Safe Merge | [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md) |

---

## 🔧 Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Keine zweite Architektur, keine Browser-Fachlogik und keine stillen Versionssprünge.

Normale PRs nach `main` werden ausschließlich über `/safe-merge` übernommen.

Details: [`AGENTS.md`](AGENTS.md) · [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) · [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md)
