# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Versionierte Runtime-Baseline:** `0.8.4-alpha.1` – bewusst unverändert; 0.8.5 ist Feature-Fortschritt, noch kein neuer Produktrelease
- **Zuletzt vollständig remote validierte Feature-Stufe:** `0.8.5-E – Hall of Tribute / sichtbares Competitive Ranking`
- **0.8.5-A Competitive Ranking:** PR #75 · Merge `b41d8f416679515307f2a580fb66b0569057836a`
- **0.8.5-B A4-Personalisierung:** PR #76 · Merge `5a9eed536d48f30cdd1f4569e9e1b1724e5ced80`
- **0.8.5-C Street Encounters:** PR #77 · Runtime `32579029076` · Presentation `32579028963` · Repository Health `32579028895` · Release Acceptance `32579028891` · Release Package `32579028890` · 0 Review-Threads · Merge `38de9f42c2908d63945db7bf25277b2f940ede6e`
- **0.8.5-D Living Districts:** PR #79 · finaler Head `fa57c7700d0c54c2ab68753ce069b14745ea7338` · Runtime `32586077024` · Presentation `32586077030` · Repository Health `32586077045` · Release Acceptance `32586077027` · Release Package `32586077025` · 0 Review-Threads · Merge `98c8b84715cc308dd1bc9fd92b7c7e56a35cc861`
- **0.8.5-E Hall of Tribute:** PR #80 · Head `2e312e2ce27bf0858b5676d56270013e24198515` · Runtime `32586394504` · Presentation `32586394533` · Repository Health `32586394437` · Release Acceptance `32586394507` · Release Package `32586394495` · 0 Review-Threads · Merge `d383a3f364c6ee8cd954041f1d324e0ace0cb357`
- **0.8.4-Abnahme:** PR #69 · Head `3d61e9d6385a0b79069132df24d655fef42b0451` · Runtime Core `32575062624` · Presentation Core `32575062602` · Repository Health `32575062620` · 0 ungelöste Review-Threads · `SAFE MERGE PASS` · Merge `28459c197489577923fadeb5f0a42d1ac1e39327`
- **Release-Abnahme:** PR #72 · Head `7fe1a39c6b69ec819fefe064a48d1647a5fa7c93` · Runtime Core `32576362896` · Presentation Core `32576362890` · Repository Health `32576362810` · Release Acceptance `32576362827` · `SAFE MERGE PASS` · Merge `72bb3024272797b27632a96559ae8abb665fff8a`
- **Erstes lokales Alpha:** PR #73 · Head `ece6c145bb07dbb2eb87170887374c4124a871f1` · Runtime Core `32576855723` · Presentation Core `32576855749` · Repository Health `32576855738` · Release Acceptance `32576855720` · Release Package `32576855768` · 0 ungelöste Review-Threads · `SAFE MERGE PASS` · Merge `3fdb5cc3d57e73734d1f594603cafdd6d06c5210`
- **Release-Artefakt:** `BUNKERFREQUENZ-0.8.4-alpha.1.zip` · SHA-256 `fccf16ee3728827ba4eba0dfd0e3cbaf844dd68c382b3c29c766f94a7ef85146` · byte-reproduzierbar · entpackter Paket-Smoke bis `completed` bestanden
- **Recovery-Härtung:** Snapshot-/Journal-Recovery bleibt vollständig regressionsgedeckt; 0.8.5-D erweitert Combined Recovery um den persistenten District-State
- **Nächster Pflichtblock:** `0.8.6-A – Property Purchase Foundation`: die bereits katalogisierten kaufbaren Orte ausschließlich über EconomyService erwerbbar machen
- **Fortschritt zum ersten spielbaren Alpha-Release:** `100 %`
- **Aktueller Release-Blocker:** keiner; `0.8.4-alpha.1` bleibt die freigegebene Runtime-Baseline, während 0.8.5-A bis E auf `main` zusätzlich remote validiert sind

## Release-Ziel ✅

Das erste lokal startbare Alpha verbindet Character Forge, Equipment/Economy, Event-Aktionen, Krisen und Settlement über bestätigte Journal-Ereignisse mit einer bedienbaren Oberfläche.

**Abnahme erfüllt:** Aus einem frischen Checkout bzw. entpackten Release-Paket kann eine Person ohne Codewissen `Crew wählen → Event planen → Equipment beschaffen → Event starten → Krise lösen oder ohne Krise fortfahren → abrechnen → speichern → neu laden/recovern` vollständig durchführen.

**Release-Hinweis:** `0.8.4-alpha.1` bleibt der letzte bewusst freigegebene Produktrelease. Die danach gemergten 0.8.5-Features erhöhen die Produktversion nicht stillschweigend; ein neuer Release braucht eine eigene Abnahme.

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

### Folgeausbau nach dem lokalen Alpha

- [x] persistente Bezirksdynamik aus bestätigten Settlement-/Street-Ergebnissen ableiten – 0.8.5-D / PR #79
- [ ] Immobilienkauf an EconomyService anbinden
- [ ] Immobilien-Ausbauzustand + Kosten-/Nutzenregeln implementieren
- [ ] hochwertigen Kartenrenderer an die read-only Projection anbinden
- [x] Hall-of-Tribute-Ranking aus bestätigten Statistiken speisen – 0.8.5-E / PR #80; lokale Ansicht erfindet keine Gegner

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
- [x] Stabilität und Heat im Settlement-Receipt bestätigt; seit 0.8.5-D werden daraus zusätzlich persistente District-Folgen abgeleitet
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

## 0.8.4 – Schreibender lokaler A4-Client ✅

- [x] A4 als kleinsten schreibenden Client ausschließlich an bestehende Application-Services anbinden
- [x] keine zweite Domain-, Economy-, Incident-, Settlement- oder Persistenzlogik im Browser erzeugen
- [x] Event-/Economy-/Incident-/Settlement-Daten ausschließlich über read-only Projection an den Client geben
- [x] Event-Availability und Blocker direkt aus `EventExecutionService.available_actions(...)` übernehmen
- [x] unbekannte Commands und unbekannte Command-Felder vor jedem Write fail-closed ablehnen
- [x] First Run `Crew → Event → Equipment → optional Krise → Settlement → Ergebnis` führen
- [x] kanonische Event-Blocker als verständliche deutsche Hilfetexte darstellen
- [x] lokalen Server ausschließlich an `127.0.0.1` binden und statisch nur `web/a4/` ausliefern
- [x] First Run nur auf leerem Journal/GENESIS erlauben und vorhandene Saves niemals überschreiben
- [x] dokumentierten Ein-Befehl-Start in `docs/A4_FIRST_RUN_ANLEITUNG.md` ergänzen
- [x] deterministischen Smoke-Test `neues Spiel → kompletter Event-Loop → Save/Snapshot → Neustart → Recovery → identischer Zustand` ergänzen
- [x] durch den Smoke gefundenen fehlenden-State/Head-Snapshot-Recovery-Randfall im zentralen Persistence-Kern beheben
- [x] eigenständige Regression für fehlenden `state/current.json` bei gültigem Snapshot ergänzen
- [x] finalen PR-#69-Head `3d61e9d6385a0b79069132df24d655fef42b0451` dreifach grün bestätigen
- [x] Runtime Core `32575062624`
- [x] Presentation Core `32575062602`
- [x] Repository Health `32575062620`
- [x] ungelöste Review-Threads = 0
- [x] zusätzlicher Codex-Code-Review angefordert; wegen externem Nutzungslimit nicht ausgeführt und nicht als Review-Pass gewertet
- [x] PR #69 ausschließlich per `/safe-merge` übernehmen
- [x] `SAFE MERGE PASS` + Main-Provenienz bestätigen
- [x] Merge `28459c197489577923fadeb5f0a42d1ac1e39327`

## Release-Abnahme – erstes lokales Alpha ✅

- [x] frischen Checkout ohne vorhandenen Save als reale Release-Ausgangslage automatisch prüfen
- [x] Klickstart/Ein-Befehl-Start des A4-Clients als echten Launcherprozess prüfen
- [x] `--no-browser` und freie Portwahl über `--port 0` abnehmen
- [x] verständliche Startfehler für fehlende Dateien, belegten Port und unbrauchbaren Save-Pfad prüfen
- [x] vollständigen First-Run/Gameplay-Pfad bis `completed` gegen den automatisierten Smoke abgleichen
- [x] Save/Neustart und identischen bestätigten Zustand prüfen
- [x] kontrollierten Recovery-Fall einschließlich fehlendem State-Checkpoint regressionsprüfen
- [x] Release-Acceptance-Evidence mit Quell-Head und Gate-Runs erzeugen
- [x] Release-Abnahme PR #72 per `/safe-merge` übernehmen
- [x] erst danach Produktversion `0.8.4-alpha.1` festlegen
- [x] finalen reproduzierbaren ZIP-/SHA-256-Artefaktlauf auf dem Release-Head bestätigen
- [x] erzeugtes Paket in frischem Zielordner erneut starten und Kernpfad smoke-testen
- [x] finalen Release-PR #73 mit allen fünf Gates grün per `/safe-merge` übernehmen
- [x] `SAFE MERGE PASS` und Main-Provenienz für Release-Merge `3fdb5cc3d57e73734d1f594603cafdd6d06c5210` bestätigen

---

# P1 – Living World nach dem lokalen Alpha

## 0.8.5 – Ranking, Personalisierung, Straße und Living Districts ✅

### 0.8.5-A – Competitive Top-10 Ranking ✅

- [x] Ranggleichstände abgeschafft; Rangnummern immer eindeutig
- [x] aktuelle Metrik bleibt primäre Autorität
- [x] bei gleichem Wert verdrängt höheres Momentum den Stillstehenden
- [x] Top-10-Druckfaktor 1,0; ab bisherigem Platz 11 nur noch 0,1
- [x] Previous-Cycle-Snapshot, Auf-/Abstieg und stabile Tiebreaker regressionsgeprüft
- [x] PR #75 per `/safe-merge` übernommen · Merge `b41d8f416679515307f2a580fb66b0569057836a`

### 0.8.5-B – A4-Personalisierung ✅

- [x] Anzeigename, Alias, mehrere Spitznamen und Motto im A4-Client editierbar
- [x] technische Character-ID bleibt unveränderlich
- [x] ausschließlich vorhandenen `CharacterProfileService` wiederverwendet
- [x] Profilwrite erhält Event-/Economy-State unverändert und ist idempotent
- [x] PR #76 per `/safe-merge` übernommen · Merge `5a9eed536d48f30cdd1f4569e9e1b1724e5ced80`

### 0.8.5-C – Replaybare Street Encounters ✅

- [x] 25 % ruhige Runde, 60 % positiv, 15 % negativ
- [x] unter tatsächlichen Begegnungen 80 % positiv / 20 % negativ
- [x] stabile Walk-ID + SHA-256-basierte Auswahl; kein Reload-Reroll
- [x] nur bestehende Energie-/Stress-/Rufeffekte; keine erfundenen Geld-/Itemgewinne
- [x] A4-Button und Ergebnisdarstellung ohne Zufallslogik im Browser
- [x] finaler Head `8fcd9866ec7b84b1040635de04329bf013632125` 5/5 grün
- [x] PR #77 per `/safe-merge` übernommen · Merge `38de9f42c2908d63945db7bf25277b2f940ede6e`

### 0.8.5-D – Living Districts ✅

- [x] persistenter `DistrictState` für alle acht Berlin-Ops-Bezirke
- [x] Heat, Prestige, Polizeidruck und Szeneaktivität auf 0..100
- [x] Settlement-Folgen nur aus bestätigtem Event + Settlement
- [x] Street-Folgen nur aus bestätigtem `street.encounter_resolved`-Journalrecord
- [x] Quellen idempotent; unbekannter Ort = sicherer No-op statt erfundener Zuordnung
- [x] Combined Recovery um District-Replay erweitert
- [x] bestehende City-Map-Projection mit persistierten District-Metriken wiederverwendet
- [x] A4-Bezirkslage read-only; Browser besitzt keine District-Balance-/Schreiblogik
- [x] zu breiter PR #78 bewusst geschlossen und durch fokussierten PR #79 ersetzt
- [x] CI fand einen echten HTTP/Python-Tuple-vs-List-Restartunterschied; auf finalem Head JSON-stabil behoben
- [x] finaler Head `fa57c7700d0c54c2ab68753ce069b14745ea7338` 5/5 grün
- [x] PR #79 per `/safe-merge` übernommen · Merge `98c8b84715cc308dd1bc9fd92b7c7e56a35cc861`

### 0.8.5-E – Hall of Tribute / sichtbares Ranking ✅

- [x] bestehende 0.8.5-A-Ranking-Engine unverändert wiederverwendet
- [x] A4-Hall mit Ruf / Level / Resonanz
- [x] Platz, `↑` Aufstieg, `↓` Abstieg, `→` gehalten, `★` neu und Top-10-Zone sichtbar
- [x] lokaler Client erfindet keine Gegner oder Netzwerkmetriken
- [x] zusätzliche Teilnehmer nur über explizit bestätigte Participant-Projections
- [x] Regression mit 12 bestätigten Teilnehmern prüft Top 10 und Challenger-Verdrängung
- [x] finaler Head `2e312e2ce27bf0858b5676d56270013e24198515` 5/5 grün
- [x] PR #80 per `/safe-merge` übernommen · Merge `d383a3f364c6ee8cd954041f1d324e0ace0cb357`

### Noch bewusst nicht Bestandteil von 0.8.5

- [ ] saisonale Wochen-/Monatszyklen und satirische Hall-of-Tribute-Titel
- [ ] echtes Netzwerk-/Telegram-Roster; lokale Hall zeigt daher nur bestätigte lokale Daten, bis weitere Teilnehmer bestätigt geliefert werden
- [ ] Immobilienkauf und Immobilienausbau
- [ ] hochwertiger Berlin-Kartenrenderer

---

# P2 – Nächster sinnvoller Ausbau

## 0.8.6-A – Property Purchase Foundation ⏭️

1. Die sieben bereits als `purchasable` katalogisierten Berlin-Ops-Orte als echte kaufbare Objekte modellieren.
2. Kauf ausschließlich über bestätigte EconomyService-Transaktionen; keine direkte UI-Besitzmutation.
3. Eigentum als eigenen kleinen State-/Journalvertrag mit Idempotenz, Replay und Recovery führen.
4. Nicht kaufbare Orte weiterhin fail-closed ablehnen.
5. Erst nach dieser Grundlage Property-Upgrades und hochwertigen Map-Renderer anbinden.

### Danach

- **0.8.6-B – Property Upgrades:** Schallschutz, Strom, Fluchtwege, Deko, Bühne, Bar, Lager, Security, Studio und Office datengetrieben ausbauen.
- **0.8.6-C – Seasonal Hall:** bestätigte Zeitzyklen, Wochen-/Monatswertung und Titel wie `Lärmadel`, `Bunkerbaron`, `Kabelkönig`, `Pegelpapst`, `Nachtminister`.
- **0.8.6-D – Berlin Ops Map PRO:** Renderer auf stabilem District-/Property-State statt vorgezogener UI-Simulation.

---

# Technische Folgeoptimierungen

- [ ] Recovery-Receipt um maschinenlesbare Fehlerkategorie und Anzahl übersprungener Snapshots erweitern.
- [x] reproduzierbaren vollständigen Event-/Incident-/Settlement-Replay-Beleg mit exaktem Head, CI-Runs und Safe-Merge-Provenienz in `reports/SETTLEMENT_VALIDATION_0.8.3-C.json` festgeschrieben.
- [x] A4 übersetzt die kanonischen Event-Blocker-IDs in sichtbare Hilfetexte, berechnet die Gates aber niemals neu.
- [x] fehlenden State bei gültigem Snapshot am Journal-Head als echte Recovery statt falschem `healthy` regressionsgetestet.
- [x] finalen Release-Receipt `reports/RELEASE_0.8.4-alpha.1.json` mit innerem Spiel-ZIP-Hash und äußerem GitHub-Artefakt-Digest getrennt dokumentiert.
- [ ] Repository Health um Abschlussabgleich gemergter Meilensteine zwischen Status/TODO/README erweitern.
- [ ] District-No-op-Replay-Receipt für unbekannte Orte semantisch auf `idempotent_replay` präzisieren; aktuell bereits sicherer No-op ohne Doppelwrite.
- [ ] A3 Event-/Incident-Blocker-IDs später ebenfalls über denselben sichtbaren Hilfetextvertrag darstellen, ohne Regeln neu zu berechnen.
- [ ] gemeinsames versioniertes Spielszenario `Planung → Beschaffung → Straße → Bezirksfolge → Krise → Abrechnung → Hall → Neustart` in die nächste Release-Gesamtbeschreibung aufnehmen.

---
