<div align="center">

# BUNKERFREQUENZ

### Beton. Bass. Berlin.

**Techno-/FreeTekno-Crew-RPG · Character Forge · Event-Management · Living Districts · Property Progression**

<p>
  <img alt="Runtime Baseline 0.8.4 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.8.4--alpha.1-ff4d00">
  <img alt="Feature Stand Runtime Owned Map E2E validiert" src="https://img.shields.io/badge/Feature_Stand-RUNTIME--OWNED--MAP--E2E_validiert-7dff00">
  <img alt="Aktive Iteration Runtime Owned Evidence Receipt" src="https://img.shields.io/badge/Aktiv-RUNTIME--OWNED--EVIDENCE-00c2ff">
  <img alt="Mergeweg Safe Merge" src="https://img.shields.io/badge/Mergeweg-%2Fsafe--merge-8a2be2">
</p>

> **Entdecken → arbeiten → ansparen → nachvollziehen → entscheiden → planen → handeln → eskalieren → abrechnen → Stadt verändern → erinnern → ausbauen → aufsteigen.**

</div>

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

---

## ⚡ Projekt-Puls

| | Aktueller Stand |
|---|---|
| **Release-Baseline** | `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease |
| **Status-Sync-Anker** | PR #181 · Merge `48f16864c319123e8ae4bcd04ba446aaa6ff153d` |
| **Validierter Feature-Stand** | ✅ `0.8.8-QA-RUNTIME-OWNED-MAP-E2E-FIXTURE` |
| **Aktive Iteration** | 🟡 `0.8.8-QA-RUNTIME-OWNED-EVIDENCE-RECEIPT` |
| **Danach** | nur konkrete Crew-Identity-Micro-Polish-Befunde aus echten E2E-Läufen bearbeiten |
| **Avatar-Kette** | ✅ Profil → bestätigtes HUD → runtime-bestätigter eigener Map-Ort → eigener Hall-/Ranking-Eintrag · Chromium + Firefox · High Contrast + kleines Fenster validiert |
| **Living World** | ✅ replaybare Street Encounters · 16 Begegnungen · vier Ansatzprofile · Grenz-/Replay-/Verteilungsaudits |
| **Ranking** | ✅ Competitive Top 10 · bestätigte Wochen-/Monatszyklen · lokale Crew-Marke nur am eigenen Eintrag |
| **Property** | ✅ 7 kaufbare Orte + 10 Ausbauarten, Level 1–3 · Runtime-Owned-Map-E2E bestätigt |
| **Berlin Ops Map** | ✅ 8 Districts · 12 Locations · read-only · lokaler Zoom/Pan · Crew-Marke an runtime-bestätigtem eigenem Besitz |
| **Scene Jobs** | ✅ persönliches Bargeld · Anti-Grind · Lohnvorschau · zwei Recovery-Wahlen |
| **Assistent** | ✅ sichere Steuerung · bestätigte Rundenausführung · Freundschafts-Nachhall |
| **Bank & Kontoauszug** | ✅ Wallet↔Bank · Sparzins · read-only TXT/CSV-Export |
| **Event-Feedback** | ✅ Street-, Recovery- und Krisen-FX nur nach bestätigter Runtime-Antwort |
| **Netzwerk/Telegram** | noch nicht implementiert; keine erfundenen Remote-Spieler |

> [!IMPORTANT]
> Die aktuelle Feature-Linie bis PR #181 wurde ausschließlich über den Repository-Workflow mit grünen Gates und `/safe-merge` nach `main` übernommen. `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json` werden zusätzlich durch den read-only Status-Sync gegen den letzten fachlich relevanten Safe Merge geprüft.

Die README ist bewusst **Navigation und Projektpuls**, keine zweite Feature-Historie. Detailstatus steht in [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json), aktive Arbeit in [`TODO.md`](TODO.md), Ausbauvorrat in [`FEATURE_POOL.md`](FEATURE_POOL.md) und historische Änderungen in `CHANGELOG.md`/`CHANGELOG.d/`.

---

## 🎮 Spielkern

BUNKERFREQUENZ ist ein lokales Techno-/FreeTekno-Crew-RPG. Bestätigte Aktionen, Ereignisse und ihre Folgen formen Charakter, Crew und Stadt.

```text
SCENE JOBS → PERSÖNLICHES BARGELD → BANK / SPAREN → KONTOAUSZUG
      ↓
STRASSE / SPIELERANSATZ
      ↓
CHARAKTER & CREW
      ↓
EVENT PLANEN → STARTEN → KRISE? → ENTSCHEIDEN → SETTLEMENT
      ↓
DISTRICT WORLD EVENTS · TIMELINE · BERLIN-ERINNERUNGEN
      ↓
LIVING DISTRICTS / BERLIN OPS MAP
      ↓
PROPERTY / HALL OF TRIBUTE
```

### Validierte Kernbereiche

- Character Forge mit 16 Skills, 165 Trait-Namen, Level 1–50 + Resonanz
- Event-State, Equipment/Economy, Krisen und Settlement
- append-only Journal, Save, Snapshot, Restart und Recovery
- deterministische Street Encounters ohne Reload-Reroll
- persistente District-Werte und cadence-geführte District World Events
- Property Purchase + dreistufige Upgrades
- Berlin Ops Map mit lokaler read-only Bedienung
- Competitive Top 10 + Wochen-/Monatszyklen
- sichtbare read-only Ereignis-Timeline und Berlin-Erinnerungen
- Crew-Logo/Fahne als kleines synchronisierbares Identitätsrezept statt Bildblob
- bestätigte Crew-Identität im Profil, HUD, auf eigenem Kartenbesitz und im eigenen Ranking-Eintrag
- gemeinsame High-Contrast-Außenkante und klare Kurzmarken-Trennung für die bestätigte Crew-Identität
- echter Chromium- und nativer Firefox-Acceptance-Pfad für Profil → HUD → runtime-bestätigten Map-Besitz → eigenen Ranking-Eintrag inklusive kleinem Fenster und Hohem Kontrast
- Scene Jobs, persönliches Bargeld, Bank, Sparzins und Kontoauszug
- Secret Best Friend Assistant auf bestehenden Scene-Job-/Rundenverträgen
- lokale Presentation-FX ausschließlich nach bestätigten Runtime-Ergebnissen

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
| Browser-UI | Auswahl-IDs und lokale Darstellung senden | Preise, Erträge, Jobfolgen, Zinsen, Rundenautorität oder Regeln autorisieren |

Ein UI-Refresh, Zoom, Filter, Avatar-Rendering oder Animation darf niemals Gameplay erneut würfeln, Jobs doppelt auszahlen oder bestätigte Fachwerte verändern.

---

## 🛡️ Persistenz & Recovery

- append-only JSONL-Journal
- SHA-256-Hashkette
- atomare State-/Meta-Writes
- Snapshots
- Replay/Recovery aus bestätigtem Journal
- Quarantäne beschädigter Journal-Tails
- Fault-Injection-Regressionen

---

## ✅ Qualitäts- und Mergeweg

```text
aktueller main enthalten
        ↓
Runtime Core ✅
Presentation Core ✅
Repository Health ✅
Status Sync ✅
Release Acceptance ✅
Release Package ✅
        ↓
0 ungelöste Review-Threads
        ↓
/safe-merge
        ↓
SAFE MERGE PASS + Main-Provenienz
```

Wichtige lokale Prüfungen:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
PYTHONPATH=src:. python3 -m unittest discover -s tests/repository -v
PYTHONPATH=. python3 -m unittest tests.quality.test_status_sync -v
PYTHONPATH=src python3 tools/repository_health.py
python3 tools/status_sync.py check
```

Der Status-Sync ist read-only: Er schreibt weder `main` noch Statusdateien automatisch um. Eine Korrektur bleibt ein normaler prüfbarer PR und wird ebenfalls über `/safe-merge` abgeschlossen.

---

## 📦 Release-Baseline

```text
BUNKERFREQUENZ-0.8.4-alpha.1.zip
SHA-256:
fccf16ee3728827ba4eba0dfd0e3cbaf844dd68c382b3c29c766f94a7ef85146
```

Feature-Fortschritt auf `main` ist kein stiller Produktrelease. Eine neue Produktversion braucht eine eigene Release-Iteration.

---

## 🗂️ Schnellzugriff

| Gesucht | Datei |
|---|---|
| Maschinenstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| aktive Arbeit | [`TODO.md`](TODO.md) |
| Ausbauvorrat | [`FEATURE_POOL.md`](FEATURE_POOL.md) |
| Projektmanifest | [`PROJEKTMANIFEST.json`](PROJEKTMANIFEST.json) |
| Status-Sync erklärt | [`docs/STATUS_SYNC_LAIENHILFE.md`](docs/STATUS_SYNC_LAIENHILFE.md) |
| Anfängerstart | [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md) |
| Crew-Logo/Fahne | [`docs/LAIENHILFE_CREW_LOGO_FAHNE.md`](docs/LAIENHILFE_CREW_LOGO_FAHNE.md) |
| Avatar im Ranking | [`docs/LAIENHILFE_CREW_AVATAR_RANKING.md`](docs/LAIENHILFE_CREW_AVATAR_RANKING.md) |
| Avatar auf der Karte | [`docs/LAIENHILFE_CREW_AVATAR_KARTE.md`](docs/LAIENHILFE_CREW_AVATAR_KARTE.md) |
| Scene Jobs & Bargeld | [`docs/LAIENHILFE_SCENE_JOBS.md`](docs/LAIENHILFE_SCENE_JOBS.md) |
| Bank, Sparen & Kontoauszug | [`docs/LAIENHILFE_BANK_UND_SPAREN.md`](docs/LAIENHILFE_BANK_UND_SPAREN.md) |
| Berlin-Erinnerungen | [`docs/LAIENHILFE_DISTRICT_BIO.md`](docs/LAIENHILFE_DISTRICT_BIO.md) |
| Berlin Ops Map | [`manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json`](manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json) |
| Safe Merge | [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md) |
| Repository-Regeln | [`AGENTS.md`](AGENTS.md) |

---

## 🔧 Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Vor dem ersten Patch wird gemäß `AGENTS.md` eine **Planned-Read-Liste** festgelegt. Basisdateien werden nur bei Vertrags-/Statusbedarf, Arbeitsdateien gezielt und Logs nur bei konkretem Fehler oder als kompakter Abschlussnachweis gelesen.

**Keine zweite Architektur, keine Browser-Fachlogik, keine stillen Versionssprünge und kein direkter normaler Merge nach `main`.** Normale PRs werden ausschließlich über `/safe-merge` übernommen.

Details: [`AGENTS.md`](AGENTS.md) · [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) · [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md)
