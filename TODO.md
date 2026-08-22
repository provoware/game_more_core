# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Versionierte Runtime-Baseline:** `0.5.2-alpha.1`
- **Zuletzt vollständig remote validierte Feature-Stufe:** `0.8.3-C – Settlement & Consequences`
- **0.8.3-C-Abnahme:** PR #65 · Head `ccfb145547b241a179bd0135d34a7470d690821c` · Runtime Core `32568683844` · Presentation Core `32568683898` · Repository Health `32568683863` · 0 ungelöste Review-Threads · `SAFE MERGE PASS` · Merge `5ae811333878ae67947417ccb72e791caafe4ba9`
- **Repository-Hygiene danach:** versehentliche leere Markerdatei ausschließlich über PR #67 entfernt · Runtime `32568910870` · Presentation `32568910892` · Repository Health `32568910865` · `SAFE MERGE PASS` · Merge `057b5131dfd5bfaf1c26ddd0a3e862fb52c0675f`; Produktbaum wieder exakt ohne Markerdatei
- **Nächster Pflichtblock:** kleinster schreibender **A4-Game-Client** auf den vorhandenen Application-Commands
- **Fortschritt zum ersten spielbaren Alpha-Release:** `96 %` (Planungswert; fachlicher Event-Loop vollständig remote validiert, Client-Anbindung und First-Run/Save-Recovery-Smoke-Test noch offen)
- **Aktueller Release-Blocker:** A4 schreibend anbinden → kompletter First-Run/Save-Recovery-Smoke-Test → erst danach Version und Release-Artefakt festlegen

## Release-Ziel

Ein lokal startbares Alpha verbindet Character Forge, Equipment/Economy, Event-Aktionen, Krisen und Settlement über bestätigte Journal-Ereignisse mit einer bedienbaren Oberfläche.

**Abnahme:** Aus einem frischen Checkout kann eine Person ohne Codewissen `Crew wählen → Event planen → Equipment beschaffen → Event starten → Krise lösen oder ohne Krise fortfahren → abrechnen → speichern → neu laden` vollständig durchführen.

**Nicht blockierend für das erste lokale Alpha:** Telegram-/Netzwerk-Sync, öffentlicher Serverbetrieb, persistente Bezirksdynamik, Immobilienausbau und native GitHub-Branch-Protection.

---

# P0 – Pflichtpfad zum ersten spielbaren Alpha

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

### Folgeausbau nach dem lokalen Alpha

- [ ] persistente Bezirksdynamik aus bestätigten Settlement-Ergebnissen ableiten
- [ ] Immobilienkauf an EconomyService anbinden
- [ ] Immobilien-Ausbauzustand + Kosten-/Nutzenregeln implementieren
- [ ] hochwertigen Kartenrenderer an die read-only Projection anbinden
- [ ] Hall-of-Tribute-Ranking aus bestätigten Statistiken speisen

## 0.8.3-C – Settlement & Consequences ✅

### Implementierung

- [x] eigenen validierten `SettlementState` + JSON-Schema angelegt
- [x] `SETTLEMENT_MANIFEST.json` als maschinenlesbaren 0.8.3-C-Vertrag angelegt
- [x] `pending_settlement` ausschließlich als bestätigte Quelle der fünf Krisenfolgen verwendet
- [x] Events ohne Krise mit deterministisch leerem Incident-State abrechenbar gemacht
- [x] Budgetfolge als eigene nicht kompensierbare `settlement`-Buchung im Economy-Ledger umgesetzt
- [x] Settlement-Buchung verändert den Markt-Tick nicht
- [x] negatives Endbudget fail-closed behandelt; kein still erfundenes Schuldenmodell
- [x] Crew-Stress über `character.resources_changed` auf `0..100` begrenzt angewandt
- [x] Ruf über replaybares `character.reputation_changed` angewandt
- [x] ältere Saves mit signiertem negativem Ruf weiterhin lesbar gehalten
- [x] neue Settlement-Ergebnisse auf Ruf-Floor `0` normalisiert und Ranking-Kompatibilität regressionsgetestet
- [x] Settlement-Receipt bindet Budget-, Stress- und Ruf-Deltas exakt an die bestätigten `effects`
- [x] Settlement-Character muss bestätigtes Crewmitglied des Events sein
- [x] Biografieeintrag mit bestätigter Top-Level-`character_id` journalisiert und projizierbar gemacht
- [x] Stabilität und Heat im Settlement-Receipt bestätigt, aber noch nicht als District-/World-State geschrieben
- [x] Incident-Historie unverändert erhalten und `pending_settlement` nach erfolgreichem Abschluss genau einmal geleert
- [x] direkten allgemeinen `settlement → completed`-Schreibweg gesperrt
- [x] `event.completed` ausschließlich nach bestätigtem Settlement erzeugt
- [x] Settlement in Combined Recovery integriert
- [x] vollständigen Pfad `Planung → Beschaffung → Equipment → Transport → Aufbau → Soundcheck → Event → optional Krise → Abbau → Settlement → completed` als Runtime-Integrationstest aufgebaut
- [x] Fault-Injection-Test für bereits durable Settlement-Journalrecords vor State-Write ergänzt
- [x] Idempotenz und falschen Event-Kontext auch beim Settlement-Replay getestet
- [x] CHANGELOG und laiengerechte Spieleranleitung auf 0.8.3-C erweitert

### Abnahme

- [x] finaler PR-#65-Head `ccfb145547b241a179bd0135d34a7470d690821c` dreifach grün bestätigt
- [x] Runtime Core `32568683844`
- [x] Presentation Core `32568683898`
- [x] Repository Health `32568683863`
- [x] alle Review-Befunde behoben; ungelöste Review-Threads = 0
- [x] zusätzlicher Codex-Review auf finalem Head angefordert; wegen externem Code-Review-Nutzungslimit nicht mehr ausgeführt und nicht als Freigabe behauptet
- [x] PR #65 ausschließlich über `/safe-merge` übernommen
- [x] `SAFE MERGE PASS` und Main-Provenienz bestätigt
- [x] Merge `5ae811333878ae67947417ccb72e791caafe4ba9`
- [x] nachgelagerte leere Markerdatei über separaten PR #67 dreifach grün entfernt und per `/safe-merge` übernommen

## Release-Kandidat – spielbarer lokaler Client ⏭️

- [x] vollständigen 0.8.3-Fachloop auf `main` als validierte Fachbasis bestätigt
- [ ] A4 als kleinsten schreibenden Client ausschließlich an bestehende Application-Commands anbinden
- [ ] keine zweite Domain-, Economy-, Incident-, Settlement- oder Persistenzlogik im Client
- [ ] Event-/Economy-/Incident-/Settlement-Projektionen als read-only Clientquelle ergänzen
- [ ] Ersteinstieg `Crew → Event → Equipment → optional Krise → Settlement → Ergebnis` führen
- [ ] verständliche Blocker-/Fehlermeldungen aus kanonischen IDs ableiten
- [ ] Start aus frischem Checkout mit einem dokumentierten Befehl nachweisen
- [ ] deterministischen Smoke-Test `neues Spiel → kompletter Event-Loop → Save → Neustart → Recovery` ergänzen
- [ ] Runtime Core + Presentation Core + Repository Health + 0 Review-Threads abnehmen
- [ ] erst danach Version, Release Notes und reproduzierbares Release-Artefakt festlegen

---

# P1 – direkt nach dem lokalen Alpha

1. **Dynamische Bezirkslage**
   - Heat, Prestige, Polizeidruck und Szeneaktivität ausschließlich aus bestätigten Settlement-/Eventergebnissen verändern.
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
- [x] reproduzierbaren vollständigen Event-/Incident-/Settlement-Replay-Beleg mit exaktem Head, CI-Runs und Safe-Merge-Provenienz in `reports/SETTLEMENT_VALIDATION_0.8.3-C.json` festgeschrieben.
- [ ] Repository Health um Abschlussabgleich gemergter Meilensteine zwischen Status/TODO/README erweitern.
- [ ] A4/A3 übersetzen Event-/Incident-Blocker-IDs in sichtbare Hilfetexte, berechnen Regeln aber niemals neu.
- [ ] Nach vollständigem 0.8.3 ein gemeinsames versioniertes Spielszenario `Planung → Beschaffung → Krise → Abrechnung` in beide Gesamtbeschreibungen aufnehmen.

---
