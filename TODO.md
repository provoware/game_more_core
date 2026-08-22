# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Versionierte Runtime-Baseline:** `0.8.4-alpha.1`
- **Zuletzt vollständig remote validierte Feature-Stufe:** `0.8.4 – Schreibender A4-Game-Client + First-Run/Recovery`
- **0.8.4-Abnahme:** PR #69 · Head `3d61e9d6385a0b79069132df24d655fef42b0451` · Runtime Core `32575062624` · Presentation Core `32575062602` · Repository Health `32575062620` · 0 ungelöste Review-Threads · `SAFE MERGE PASS` · Merge `28459c197489577923fadeb5f0a42d1ac1e39327`
- **Release-Abnahme:** PR #72 · Head `7fe1a39c6b69ec819fefe064a48d1647a5fa7c93` · Runtime Core `32576362896` · Presentation Core `32576362890` · Repository Health `32576362810` · Release Acceptance `32576362827` · `SAFE MERGE PASS` · Merge `72bb3024272797b27632a96559ae8abb665fff8a`
- **Erstes lokales Alpha:** PR #73 · Head `ece6c145bb07dbb2eb87170887374c4124a871f1` · Runtime Core `32576855723` · Presentation Core `32576855749` · Repository Health `32576855738` · Release Acceptance `32576855720` · Release Package `32576855768` · `SAFE MERGE PASS` · Merge `3fdb5cc3d57e73734d1f594603cafdd6d06c5210`
- **Release-Artefakt:** `BUNKERFREQUENZ-0.8.4-alpha.1.zip` · SHA-256 `fccf16ee3728827ba4eba0dfd0e3cbaf844dd68c382b3c29c766f94a7ef85146` · byte-reproduzierbar · entpackter Paket-Smoke bis `completed` bestanden
- **Fortschritt zum ersten spielbaren Alpha-Release:** `100 %`
- **Nächster Pflichtblock:** `0.8.5 – Dynamische Bezirkslage` aus bestätigten Settlement-/Event-Ergebnissen; keine neue Produktversion vor eigener Abnahme

## Release-Ziel ✅

Das erste lokal startbare Alpha verbindet Character Forge, Equipment/Economy, Event-Aktionen, Krisen und Settlement über bestätigte Journal-Ereignisse mit einer bedienbaren Oberfläche.

**Abnahme erfüllt:** Aus einem frischen Checkout bzw. entpackten Release-Paket kann der Pfad `Crew wählen → Event planen → Equipment beschaffen → Event starten → optional Krise lösen → abrechnen → speichern → neu laden/recovern` bestätigt durchlaufen werden.

**Nicht Bestandteil von 0.8.4-alpha.1:** Telegram-/Netzwerk-Sync, öffentlicher Serverbetrieb, persistente Bezirksdynamik, Immobilienausbau und native GitHub-Branch-Protection.

---

# P0 – Pflichtpfad zum ersten spielbaren Alpha ✅

## 0.8.1 – Event State Foundation ✅

- [x] EventState, Ort, Budget, Acts, Crew, Equipment-Readiness, Zeitfenster und Safety definiert
- [x] Event-Journal, Revision, Idempotenz und Recovery implementiert
- [x] PR #48 dreifach grün und gemergt

## 0.8.2 – Equipment & Economy ✅

- [x] Katalog, Besitz, Reservierung und Marktpreise getrennt modelliert
- [x] Kaufen, Verkaufen, Verbrauchen und Kompensation journalfähig
- [x] Event-Budget nur über bestätigte Economy-Transaktionen veränderbar
- [x] Event-Kontext- und Same-Revision-Replay-Integrität gehärtet
- [x] PR #61 dreifach grün und gemergt

## 0.8.3-A – Event Execution Engine ✅

- [x] acht kanonische Event-Aktionen von `draft` bis `settlement`
- [x] zentrale Voraussetzungen für Acts, Crew, Budget, Equipment, Ort, Zugang, Zeitfenster und Safety
- [x] Availability-Projektion mit Blocker-IDs statt Client-Doppellogik
- [x] persistierten Eventzustand als alleinige Autorität erzwingen
- [x] PR #62 dreifach grün und über `/safe-merge` übernommen

## 0.8.3-B1 – Crisis / Incident Engine ✅

- [x] eigener persistierter `IncidentState`
- [x] sechs Incident-Typen mit je drei Reaktionen
- [x] Severity 1–5 deterministisch
- [x] `live → crisis → live/teardown/cancelled` atomar journalisiert
- [x] `pending_settlement` als bestätigte, noch nicht direkt gebuchte Folgen
- [x] Idempotenz, Vertragsversionsschutz und Recovery gehärtet
- [x] PR #63 final dreifach grün, alle sechs Review-Threads gelöst und per `/safe-merge` übernommen

## 0.8.3-B2 – Berlin Ops Map Foundation ✅

- [x] 8 Bezirke, 12 Spielorte, 7 kaufbare Objekte und eine Hall of Tribute katalogisiert
- [x] stilisierte 0–100-Karte statt Navigations-/Adresslogik
- [x] Score-/Tier-Projektion und District-Metriken vorbereitet
- [x] unbekannte District-Overrides und ungültige Ownership fail-closed
- [x] Ausbau-Slots und Reduced-Motion-Vertrag vorbereitet

## 0.8.3-C – Settlement & Consequences ✅

- [x] eigener validierter `SettlementState` + JSON-Schema
- [x] `SETTLEMENT_MANIFEST.json` als maschinenlesbarer Vertrag
- [x] bestätigte Incident-Folgen genau einmal verbuchen
- [x] Events ohne Krise abrechenbar
- [x] Budgetfolge über Economy-Ledger
- [x] Stress/Ruf über Character-Events
- [x] negatives Endbudget fail-closed
- [x] Settlement-Receipt bindet Budget-, Stress- und Ruf-Deltas an `effects`
- [x] Incident-Historie erhalten und `pending_settlement` genau einmal leeren
- [x] `event.completed` ausschließlich über Settlement
- [x] Combined Recovery + Fault Injection
- [x] PR #65 final dreifach grün, `SAFE MERGE PASS`, Merge `5ae811333878ae67947417ccb72e791caafe4ba9`

## 0.8.4 – Schreibender lokaler A4-Client ✅

- [x] A4 ausschließlich an bestehende Application-Services anbinden
- [x] keine zweite Domain-/Economy-/Incident-/Settlement-Logik im Browser
- [x] read-only Projection für bestätigten Zustand
- [x] Event-Availability direkt aus `EventExecutionService.available_actions(...)`
- [x] unbekannte Commands/Felder fail-closed
- [x] First Run `Crew → Event → Equipment → optional Krise → Settlement → Ergebnis`
- [x] verständliche deutsche Blockertexte
- [x] localhost-only und statisch nur `web/a4/`
- [x] bestehende Saves niemals überschreiben
- [x] Ein-Befehl-Start dokumentieren
- [x] kompletter Save/Restart/Recovery-Smoke
- [x] fehlenden-State/Head-Snapshot-Randfall im Persistence-Kern beheben
- [x] PR #69 final dreifach grün, `SAFE MERGE PASS`, Merge `28459c197489577923fadeb5f0a42d1ac1e39327`

## Release-Abnahme – erstes lokales Alpha ✅

- [x] frischen Checkout ohne vorhandenen Save prüfen
- [x] echten Launcherprozess prüfen
- [x] `--no-browser` und `--port 0` abnehmen
- [x] verständliche Fehler für fehlende Dateien, belegten Port und unbrauchbaren Save-Pfad prüfen
- [x] vollständigen First-Run/Gameplay-Pfad bis `completed` prüfen
- [x] Save/Neustart und Recovery prüfen
- [x] Release-Acceptance-Evidence erzeugen
- [x] PR #72 per `/safe-merge` übernehmen
- [x] danach Produktversion `0.8.4-alpha.1` festlegen
- [x] reproduzierbares ZIP + SHA-256 erzeugen
- [x] Paket zweimal byte-identisch bauen
- [x] Paket in frischem Zielordner entpacken und über `START_BUNKERFREQUENZ.sh` starten
- [x] entpackten Kernpfad bis `completed` + Checkpoint smoke-testen
- [x] finalen Release-Head mit fünf Gates grün bestätigen
- [x] PR #73 per `/safe-merge` übernehmen
- [x] `SAFE MERGE PASS` + Main-Provenienz bestätigen

---

# P1 – direkt nach dem lokalen Alpha

## 0.8.5 – Dynamische Bezirkslage ⏭️

1. **Persistenter District-State**
   - Heat, Prestige, Polizeidruck und Szeneaktivität je Bezirk als kanonischen State modellieren.
   - Änderungen ausschließlich aus bestätigten Settlement-/Event-Ergebnissen ableiten.
   - Replay, Idempotenz und Save/Recovery von Anfang an mitführen.

2. **Immobilien-Ausbaupfade**
   - Schallschutz, Strom, Fluchtwege, Deko, Bühne, Bar, Lager und Sicherheitsraum mit Leveln, Kosten und Effekten versehen.
   - Kauf/Upgrade ausschließlich über Economy-Transaktionen.

3. **Hall of Tribute + saisonales Ranking**
   - bestätigte Wochen-/Monatsstatistiken projizieren.
   - satirische Titel wie `Lärmadel`, `Bunkerbaron`, `Kabelkönig`, `Pegelpapst` oder `Nachtminister` vergeben.
   - Animation nur als Darstellung; Reduced Motion erhält vollständige statische Information.

4. Hochwertigen Berlin-Kartenrenderer erst an stabilen District-/Property-State anbinden.
5. Native GitHub-Branch-Protection/Ruleset aktivieren, sobald ein geeigneter Admin-Schreibweg verfügbar ist.
6. `0.9 Network / Telegram Sync` als getrennten Server-/Transportvertrag planen.

---

# Technische Folgeoptimierungen

- [ ] Recovery-Receipt um maschinenlesbare Fehlerkategorie und Anzahl übersprungener Snapshots erweitern.
- [x] vollständigen Event-/Incident-/Settlement-Replay-Beleg in `reports/SETTLEMENT_VALIDATION_0.8.3-C.json` festgeschrieben.
- [x] A4 übersetzt kanonische Event-Blocker-IDs, berechnet die Gates aber niemals neu.
- [x] fehlenden State bei gültigem Snapshot am Journal-Head regressionsgetestet.
- [x] finalen Release-Receipt `reports/RELEASE_0.8.4-alpha.1.json` angelegt.
- [ ] Repository Health um Abschlussabgleich gemergter Meilensteine zwischen Status/TODO/README erweitern.
- [ ] A3 Event-/Incident-Blocker-IDs später über denselben Hilfetextvertrag darstellen.
- [ ] versioniertes Spielszenario `Planung → Beschaffung → Krise → Abrechnung → Neustart` in beide Gesamtbeschreibungen aufnehmen.

---
