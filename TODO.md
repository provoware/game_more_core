# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Versionierte Runtime-Baseline:** `0.5.2-alpha.1`
- **Zuletzt vollständig remote validierte Feature-Stufe:** `0.8.3-B – Crisis Engine + Berlin Ops Map Foundation`
- **0.8.3-B-Abnahme:** PR #63 · Head `4a83cecc7298078a9040ea94e7994ac0b2ab5558` · Runtime Core `32559629560` · Presentation Core `32559629773` · Repository Health `32559629667` · `SAFE MERGE PASS` · Merge `816a3f1dd83d9396550d702c0ac85ba98ed069dd`
- **Nächster Pflichtblock:** `0.8.3-C – Settlement & Consequences`
- **Fortschritt zum ersten spielbaren Alpha-Release:** `90 %` (Planungswert; Eventaktionen und Krisen validiert, Settlement und schreibender Client noch offen)
- **Aktueller Release-Blocker:** 0.8.3-C Settlement/Folgen → vollständigen Event-Loop abnehmen → schreibenden A4-Client anbinden

## Release-Ziel

Ein lokal startbares Alpha verbindet Character Forge, Equipment/Economy, Event-Aktionen, Krisen und Settlement über bestätigte Journal-Ereignisse mit einer bedienbaren Oberfläche.

**Abnahme:** Aus einem frischen Checkout kann eine Person ohne Codewissen `Crew wählen → Event planen → Equipment beschaffen → Event starten → Krise lösen → abrechnen → speichern → neu laden` vollständig durchführen.

**Nicht blockierend für das erste lokale Alpha:** Telegram-/Netzwerk-Sync, öffentlicher Serverbetrieb, persistente Bezirksdynamik und native GitHub-Branch-Protection.

---

# P0 – Pflichtpfad zum ersten spielbaren Alpha

## 0.8.1 – Event State Foundation ✅

- [x] EventState, Ort, Budget, Acts, Crew, Equipment-Readiness, Zeitfenster und Safety definiert
- [x] Phasenmaschine `draft → planning → procurement → transport → setup → soundcheck → live/crisis → teardown → settlement → completed`
- [x] Event-Journal, Revision, Idempotenz und Recovery implementiert
- [x] PR #48 dreifach grün und gemergt

## 0.8.2 – Equipment & Economy ✅

- [x] Katalog, Besitz, Reservierung und Marktpreise getrennt modelliert
- [x] Kaufen, Verkaufen, Verbrauchen und Kompensation journalfähig
- [x] Event-Budget nur über bestätigte Economy-Transaktionen veränderbar
- [x] Equipment-Readiness an bestätigte Reservierung gebunden
- [x] Event-Kontext- und Same-Revision-Replay-Integrität gehärtet
- [x] PR #61 dreifach grün und gemergt

## 0.8.3-A – Event Execution Engine ✅

- [x] acht kanonische Event-Aktionen von `draft` bis `settlement`
- [x] zentrale Voraussetzungen für Acts, Crew, Budget, Equipment, Ort, Zugang, Zeitfenster und Safety
- [x] Availability-Projektion mit Blocker-IDs statt Client-Doppellogik
- [x] persistierten Eventzustand als alleinige Autorität erzwingen
- [x] normale Command-Replays auch nach Phasenwechsel idempotent
- [x] PR #62 auf exaktem Head dreifach grün
- [x] `/safe-merge` = PASS · Merge `8a5b08b5f44e334298cf226510f99abbc115b3df`

## 0.8.3-B1 – Crisis / Incident Engine ✅

### Implementierung

- [x] eigenen `IncidentState` neben Event/Economy angelegt
- [x] höchstens einen aktiven Incident zugelassen
- [x] sechs Incident-Typen mit je drei Reaktionsoptionen katalogisiert
- [x] Severity 1–5 deterministisch auf Einzeleffekte skaliert
- [x] kumulierte Settlement-Summen dürfen mehrere Incidents ohne künstliche ±100-Grenze addieren
- [x] `live → crisis` atomar mit `event.incident_started` committen
- [x] Response-Auswahl + `crisis → live/teardown/cancelled` atomar auflösen
- [x] `event.incident_resolved` journalfähig und replaybar gemacht
- [x] Krisenfolgen als `pending_settlement` gesammelt, ohne Economy-/Character-Verträge zu umgehen
- [x] falsche Response, parallelen Incident und falschen Event-Kontext fail-closed behandelt
- [x] Open/Resolve auch nach State-Fortschritt idempotent
- [x] Incident-Replay validiert Event-Kontext erneut
- [x] offener Incident kann nicht mit abweichendem Vertragsstand aufgelöst werden
- [x] Fault-Injection-Recovery für durable Incident-Commits getestet
- [x] Incident-Replay in `GameRecoveryService` integriert

### Abnahme

- [x] finaler PR-#63-Head `4a83cecc7298078a9040ea94e7994ac0b2ab5558` dreifach grün
- [x] Runtime Core `32559629560`
- [x] Presentation Core `32559629773`
- [x] Repository Health `32559629667`
- [x] alle sechs Review-Threads gelöst
- [x] `/safe-merge` = PASS
- [x] Merge `816a3f1dd83d9396550d702c0ac85ba98ed069dd`

## 0.8.3-B2 – Berlin Ops Map Foundation ✅

### Datenbasis

- [x] `CITY_MAP_MANIFEST.json` als einzige Karten-Fachquelle angelegt
- [x] stilisierte 0–100-Koordinaten verwendet; keine Navigation und keine exakten Adressen
- [x] 8 Berliner Bezirke als Startzonen definiert
- [x] 12 Spielorte mit Prestige, Audience Pull, Risk, Underground Factor und Utility angelegt
- [x] 7 kaufbare Immobilien/Objekte mit Preisen und Ausbau-Slots vorbereitet
- [x] genau eine `Hall of Tribute` als Ranking-/Prestige-Sonderort definiert
- [x] Score- und Tier-System `standard / strong / prime / legendary` abgeleitet
- [x] read-only `city_map_projection` mit Top-5, Ownership und Hall-of-Tribute-Projektion implementiert
- [x] Heat, Prestige, Polizeidruck und Szeneaktivität als District-Metriken vorbereitet
- [x] unbekannte District-Overrides werden fail-closed abgewiesen
- [x] Ownership akzeptiert ausschließlich tatsächlich kaufbare Locations
- [x] Schallschutz, Strom, Fluchtwege, Deko, Bühne, Bar, Lager und Sicherheitsraum als Ausbaugrundlage katalogisiert
- [x] Reduced-Motion-Fallback im visuellen Vertrag festgelegt

### Folgeausbau nach dem vollständigen Event-Loop

- [ ] persistente Bezirksdynamik aus bestätigten Events ableiten
- [ ] Immobilienkauf an EconomyService anbinden
- [ ] Immobilien-Ausbauzustand + Kosten-/Nutzenregeln implementieren
- [ ] hochwertige Kartenoberfläche/Renderer an die read-only Projection anbinden
- [ ] Hall-of-Tribute-Ranking aus bestätigten Statistiken speisen
- [ ] saisonale Titel/Awards mit statischem Reduced-Motion-Fallback projizieren

## 0.8.3-C – Settlement & Consequences ⏭️

- [ ] `pending_settlement` aus Incidents über zuständige Economy-/Character-Wege verbuchen
- [ ] Einnahmen/Ausgaben ausschließlich aus bestätigten Event-/Economy-Daten ableiten
- [ ] Ruf-, Stress-, Stabilitäts- und Heat-Folgen atomar anwenden
- [ ] bedeutende Krisen-/Eventergebnisse in die dynamische Biografie übernehmen
- [ ] `event.completed` erst nach vollständig bestätigtem Settlement erzeugen
- [ ] vollständigen Pfad `Planung → Einkauf → Transport → Aufbau → Soundcheck → Event → Krise → Abbau → Abrechnung` testen
- [ ] Fault-Injection-Test über Krise + Settlement + Recovery ergänzen
- [ ] A4/A3 um Event-/Economy-/Incident-Projektionen erweitern, ohne Domain-State direkt zu schreiben

## Release-Kandidat – spielbarer lokaler Client ⏭️

- [ ] vollständigen 0.8.3-Loop auf einem exakten Head lokal und remote bestätigen
- [ ] A4 als kleinsten schreibenden Client an bestehende Application-Commands anbinden
- [ ] keine zweite Domain-, Economy-, Incident- oder Persistenzlogik im Client
- [ ] Ersteinstieg `Crew → Event → Equipment → Krise → Settlement → Ergebnis` führen
- [ ] verständliche Blocker-/Fehlermeldungen aus kanonischen IDs ableiten
- [ ] Start aus frischem Checkout mit einem dokumentierten Befehl nachweisen
- [ ] deterministischen Smoke-Test `neues Spiel → kompletter Event-Loop → Save → Neustart → Recovery` ergänzen
- [ ] Runtime Core + Presentation Core + Repository Health + 0 Review-Threads abnehmen
- [ ] erst danach Version, Release Notes und reproduzierbares Release-Artefakt festlegen

---

# P1 – direkt nach dem lokalen Alpha

1. **Dynamische Bezirkslage**
   - Heat, Prestige, Polizeidruck und Szeneaktivität ausschließlich aus bestätigten Ereignissen verändern.
   - Auswirkungen auf Eventchancen, Kosten und Risiko datengetrieben ableiten.

2. **Immobilien-Ausbaupfade**
   - Schallschutz, Strom, Fluchtwege, Deko, Bühne, Bar, Lager und Sicherheitsraum mit Leveln, Kosten und Effekten versehen.
   - Kauf/Upgrade ausschließlich über Economy-Transaktionen.

3. **Hall of Tribute + saisonales Ranking**
   - bestätigte Wochen-/Monatsstatistiken projizieren.
   - satirische Titel wie `Lärmadel`, `Bunkerbaron`, `Kabelkönig`, `Pegelpapst` oder `Nachtminister` vergeben.
   - Animation nur als Darstellung; Reduced Motion erhält vollständige statische Information.

4. Native GitHub-Branch-Protection/Ruleset aktivieren, sobald ein geeigneter Admin-Schreibweg verfügbar ist.
5. `0.9 Network / Telegram Sync` als getrennten Server-/Transportvertrag planen.

---

# Technische Folgeoptimierungen

- [ ] Recovery-Receipt um maschinenlesbare Fehlerkategorie und Anzahl übersprungener Snapshots erweitern.
- [ ] reproduzierbaren Economy-/Event-/Incident-Replay-Beleg mit festem Seed und Head-SHA erzeugen.
- [ ] Repository Health um Abschlussabgleich gemergter Meilensteine zwischen Status/TODO/README erweitern.
- [ ] A4/A3 übersetzen Event-/Incident-Blocker-IDs in sichtbare Hilfetexte, berechnen Regeln aber niemals neu.
- [ ] Nach vollständigem 0.8.3 ein gemeinsames versioniertes Spielszenario `Planung → Beschaffung → Krise → Abrechnung` in beide Gesamtbeschreibungen aufnehmen.

---

# Abgeschlossene Meilensteine

- [x] **0.4.0** Architekturvertrag + Character Forge Foundation
- [x] **0.4.1** Trait Engine + Progression + Simulation
- [x] **0.4.2** Persistence-Vertrag
- [x] **0.4.3** UI/UX Blueprint
- [x] **0.4.4** Gameplay Action Contract
- [x] **0.5.0–0.5.2** Runtime, Recovery, Trait-/Resonanzwirkung
- [x] **0.6.0–0.6.5** Presentation, A4/A3, Ranking-/Network-Foundation
- [x] **0.7.1–0.7.2** spielbarer Character-Forge-Vertical-Slice
- [x] **0.8.1** Event State Foundation
- [x] **0.8.2** Equipment & Economy
- [x] **0.8.3-A** Event Execution Engine
- [x] **0.8.3-B** Crisis Engine + Berlin Ops Map Foundation
