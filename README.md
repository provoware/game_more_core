<div align="center">

# BUNKERFREQUENZ

### Beton. Bass. Berlin.

**Techno-/FreeTekno-Crew-RPG · Character Forge · Event-Management · Living Districts · Property Progression**

<p>
  <img alt="Runtime Baseline 0.8.4 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.8.4--alpha.1-ff4d00">
  <img alt="Feature Stand District Micro Story 002 validiert" src="https://img.shields.io/badge/Feature_Stand-DISTRICT--MICRO--STORY--002_validiert-7dff00">
  <img alt="Aktive Iteration District Chain Runtime Browser E2E" src="https://img.shields.io/badge/Aktiv-DISTRICT--CHAIN--RUNTIME--BROWSER--E2E-00c2ff">
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
| **Status-Sync-Anker** | PR #204 · Merge `a03cf981b352064415e4cbf1fc3a8f88f34beed6` |
| **Validierter Feature-Stand** | ✅ `0.8.8-STORY-DISTRICT-MICRO-STORY-002` |
| **Aktive Iteration** | 🟡 `0.8.8-QA-DISTRICT-CHAIN-RUNTIME-BROWSER-E2E` |
| **Danach** | Story-Tonbalance erst nach vollständigem E2E-Beweis weiter ausbauen |
| **District-Ereigniskette 001** | ✅ `district.power_flicker` → späterer `power_flicker_afterglow` · Exactly-once · keine Balancewirkung · Ursache read-only sichtbar |
| **District-Ereigniskette 002** | ✅ `district.temporary_space_opens` → späterer `temporary_space_afterimage` · **„Die Tür ist zu – die Adresse lebt weiter.“** · gleicher Contract V1 |
| **District-Chain-E2E** | 🟡 nächster QA-Slice: beide echten Ketten gemeinsam durch Runtime → Journal/Persistenz → Projection → Browser beweisen |
| **Avatar-Kette** | ✅ Profil → bestätigtes HUD → runtime-bestätigter eigener Map-Ort → eigener Hall-/Ranking-Eintrag · Chromium + Firefox · High Contrast + kleines Fenster validiert |
| **Crew-Lesbarkeit** | ✅ HUD-, Map- und Ranking-Kurzmarken werden im echten Chromium-/Firefox-Harness gegen `0.34rem` und zusätzlich gegen reale Textabschneidung geprüft |
| **Runtime-Owned Evidence** | ✅ derselbe bestätigte `property.purchase` ist in der vorhandenen Browser-Evidence an Location-, Event- und Ledger-Referenzen gebunden |
| **Living World** | ✅ replaybare Street Encounters · 16 Begegnungen · vier Ansatzprofile · zwei District-Micro-Stories auf einem gemeinsamen Follow-up-Vertrag |
| **Ranking** | ✅ Competitive Top 10 · bestätigte Wochen-/Monatszyklen · lokale Crew-Marke nur am eigenen Eintrag |
| **Property** | ✅ 7 kaufbare Orte + 10 Ausbauarten, Level 1–3 · Runtime-Owned-Map-E2E bestätigt |
| **Berlin Ops Map** | ✅ 8 Districts · 12 Locations · read-only · lokaler Zoom/Pan · Randfall geprüft · `1:1` stellt Gesamtansicht wieder her |
| **Scene Jobs** | ✅ persönliches Bargeld · Anti-Grind · Lohnvorschau · zwei Recovery-Wahlen |
| **Assistent** | ✅ sichere Steuerung · bestätigte Rundenausführung · Freundschafts-Nachhall |
| **Bank & Kontoauszug** | ✅ Wallet↔Bank · Sparzins · read-only TXT/CSV-Export |
| **Event-Feedback** | ✅ Street-, Recovery- und Krisen-FX nur nach bestätigter Runtime-Antwort |
| **Netzwerk/Telegram** | noch nicht implementiert; keine erfundenen Remote-Spieler |

> [!IMPORTANT]
> Die aktuelle Feature-Linie bis PR #204 wurde ausschließlich über den Repository-Workflow mit grünen Gates und `/safe-merge` nach `main` übernommen. `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json` werden zusätzlich durch den read-only Status-Sync gegen den letzten fachlich relevanten Safe Merge geprüft.

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
- bestätigte District-Parent-Evidenz plus katalogisierter Child-Eventvertrag `world.district_followup_resolved`
- Micro-Story 001: `district.power_flicker` → späterer `power_flicker_afterglow`
- Micro-Story 002: `district.temporary_space_opens` → späterer `temporary_space_afterimage`
- beide Storys bleiben im selben Bezirk, Exactly-once, ohne eigene Balanceeffekte und verwenden denselben Resolver; pro bestätigtem District-Zyklus höchstens ein offener Nachhall
- bestätigte Parent→Child-Kausalität wird in der vorhandenen Timeline read-only als `Folge von: …` erklärt; fehlende oder bezirksfremde Parents werden nicht erfunden
- Property Purchase + dreistufige Upgrades
- Berlin Ops Map mit lokaler read-only Bedienung und validiertem `1:1`-Rückweg aus dem begrenzten Randfokus
- Competitive Top 10 + Wochen-/Monatszyklen
- sichtbare read-only Ereignis-Timeline und Berlin-Erinnerungen
- Crew-Logo/Fahne als kleines synchronisierbares Identitätsrezept statt Bildblob
- bestätigte Crew-Identität im Profil, HUD, auf eigenem Kartenbesitz und im eigenen Ranking-Eintrag
- gemeinsame High-Contrast-Außenkante und klare Kurzmarken-Trennung für die bestätigte Crew-Identität
- echter Chromium- und nativer Firefox-Acceptance-Pfad für Profil → HUD → runtime-bestätigten Map-Besitz → eigenen Ranking-Eintrag inklusive kleinem Fenster und Hohem Kontrast
- kompakte HUD-, Map- und Ranking-Kurzmarken mit browserberechnet geprüftem `0.34rem`-Lesbarkeitsboden und realer Clipping-Prüfung
- bestehende Desktop-Browser-Evidence bindet denselben runtime-bestätigten Property-Kauf read-only an Location-, Event- und Ledger-Referenzen
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
| District-Kettenaudit | [`docs/DISTRICT_EVENT_CHAIN_CONTRACT_AUDIT.md`](docs/DISTRICT_EVENT_CHAIN_CONTRACT_AUDIT.md) |
| District-Chain Contract V1 | [`docs/DISTRICT_CHAIN_CONTRACT_V1.md`](docs/DISTRICT_CHAIN_CONTRACT_V1.md) |
| District-Micro-Story 001 | [`docs/DISTRICT_CHAIN_MICRO_STORY_001.md`](docs/DISTRICT_CHAIN_MICRO_STORY_001.md) |
| District-Micro-Story 002 | [`docs/DISTRICT_CHAIN_MICRO_STORY_002.md`](docs/DISTRICT_CHAIN_MICRO_STORY_002.md) |
| Ereignis-Timeline | [`docs/EVENT_TIMELINE_LAIENHILFE.md`](docs/EVENT_TIMELINE_LAIENHILFE.md) |
| Berlin Ops Map | [`manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json`](manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json) |
| Safe Merge | [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md) |
| Repository-Regeln | [`AGENTS.md`](AGENTS.md) |

---

## 🔧 Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Vor dem ersten Patch wird gemäß `AGENTS.md` eine **Planned-Read-Liste** festgelegt. Basisdateien werden nur bei Vertrags-/Statusbedarf, Arbeitsdateien gezielt und Logs nur bei konkretem Fehler oder als kompakter Abschlussnachweis gelesen.

**Keine zweite Architektur, keine Browser-Fachlogik, keine stillen Versionssprünge und kein direkter normaler Merge nach `main`.** Normale PRs werden ausschließlich über `/safe-merge` übernommen.

Details: [`AGENTS.md`](AGENTS.md) · [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) · [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md)