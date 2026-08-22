# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – weiterhin letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.6-B – Property Upgrades`
- **0.8.6-A Property Purchase:** PR #82 · Head `af582597fa2a899ab0cc0d062e128ec6b0e7dc1a` · Merge `192b3eb4ad9dc4272eafeddc8604f7265bdd30fa`
- **0.8.6-B Property Upgrades:** PR #83 · Head `acbf6b1c5615137664ed4ad84fb0535bea297030` · Runtime `32589287044` · Presentation `32589287132` · Repository Health `32589287056` · Release Acceptance `32589287152` · Release Package `32589287135` · 0 Review-Threads · `SAFE MERGE PASS` · Merge `0b301bc9004f60dbc3ce221a7c6b3e462766b5b7`
- **Erstes lokales Alpha:** `0.8.4-alpha.1` · ZIP SHA-256 `fccf16ee3728827ba4eba0dfd0e3cbaf844dd68c382b3c29c766f94a7ef85146`
- **Nächster Pflichtblock:** `0.8.6-C – Berlin Ops Map PRO`
- **Release-Blocker:** keiner für `0.8.4-alpha.1`; ein neuer Produktrelease benötigt weiterhin eine eigene Release-Abnahme

---

# Abgeschlossen ✅

## 0.8.1 – Event State Foundation

- [x] EventState, Ort, Budget, Acts, Crew, Equipment, Zeitfenster und Safety
- [x] Revision, Idempotenz, Journal und Combined Recovery

## 0.8.2 – Equipment & Economy

- [x] Katalog, Inventar, Reservierung und deterministische Marktpreise
- [x] Budgetänderungen ausschließlich über bestätigte Economy-Transaktionen
- [x] Kompensation nur für zulässige Equipment-Käufe/-Verkäufe

## 0.8.3 – Event, Krise und Settlement

- [x] 8 kanonische Event-Aktionen
- [x] Incident/Crisis Engine mit 6 Krisentypen
- [x] atomarer Settlement-Abschluss einschließlich Budget, Stress, Ruf und Biografie
- [x] vollständiger Eventpfad bis `completed`

## 0.8.4 – Schreibender lokaler A4-Client

- [x] localhost-only Game Client
- [x] keine zweite Domainlogik im Browser
- [x] First Run, Save, Snapshot, Restart und Recovery
- [x] reproduzierbares `0.8.4-alpha.1`-Paket

## 0.8.5 – Living World

- [x] **A:** Competitive Displacement Ranking
- [x] **B:** A4-Profilpersonalisierung
- [x] **C:** replaybare Street Encounters
- [x] **D:** persistente Living Districts
- [x] **E:** Hall of Tribute / sichtbare Top 10

## 0.8.6-A – Property Purchase Foundation ✅

- [x] sieben bereits katalogisierte kaufbare Berlin-Ops-Orte an echten Schreibpfad anbinden
- [x] `property.purchase` akzeptiert nur `location_id`; Preis/Owner/Budgetdelta sind keine Client-Autorität
- [x] Kaufpreis ausschließlich aus `CITY_MAP_MANIFEST.purchase_price_cents`
- [x] Economy-Ledger-Kind `property_purchase`
- [x] Economy + Event-Budget + PropertyState in **einem atomaren Commit**
- [x] `world.property_purchased` append-only journalisieren
- [x] Combined Recovery für Economy/Event/Eigentum
- [x] nicht kaufbare Orte und Doppelkäufe fail-closed
- [x] A4 und Berlin-Ops-Projection zeigen bestätigten Besitz
- [x] Fault-Injection, Idempotenz und Command-Injection regressionsprüfen
- [x] PR #82 5/5 grün und per `/safe-merge` übernommen

## 0.8.6-B – Property Upgrades ✅

- [x] eigenen rückwärtskompatiblen `PropertyUpgradeState` einführen
- [x] zehn vorhandene Ausbauarten nutzen; keine Parallelkataloge
- [x] Level `1–3` mit Kostenmultiplikatoren `1.00 / 1.50 / 2.25`
- [x] Ausbaukosten aus bestätigtem ursprünglichem Immobilienkaufpreis ableiten
- [x] `property.upgrade` akzeptiert nur `location_id + upgrade_id`
- [x] Client darf Kosten, Level, Deltas und Menge nicht bestimmen
- [x] Economy-Ledger-Kind `property_upgrade`; kein Equipment-Market-Tick
- [x] Economy + Event-Budget + Upgrade-State atomar bestätigen
- [x] `world.property_upgraded` replaybar journalisieren
- [x] Combined Recovery einschließlich Fault nach durablem Journal
- [x] effektive Standortwerte auf `0..100` begrenzen
- [x] bestehenden City-Map-Score/Tier für Ausbauwirkung wiederverwenden
- [x] A4 zeigt Level, nächsten bestätigten Preis und effektive Werte
- [x] Max-Level, Eigentum, Slot, Budget, Idempotenz und Manipulationsversuche regressionsprüfen
- [x] PR #83 5/5 grün, 0 Review-Threads, `SAFE MERGE PASS`

---

# AKTIV / NÄCHSTER PFLICHTBLOCK

## 0.8.6-C – Berlin Ops Map PRO 🗺️

### Ziel

Eine hochwertige, unmittelbar verständliche Kartenansicht auf den **bereits bestätigten** Daten aufbauen. Der Renderer ist reine Presentation und besitzt keinerlei eigene Spiellogik.

### C1 – Kartenvertrag und Datenadapter

- [ ] vorhandene `city_map_projection` als einzige fachliche Kartenquelle festschreiben
- [ ] Renderer-View-Model für Districts, Locations, Eigentum, Ausbaulevel, Score/Tier und Hall ableiten
- [ ] keinerlei direkte Domain-/Save-Writes aus der Karte zulassen
- [ ] unbekannte IDs und unvollständige Projection fail-closed behandeln

### C2 – Visuelle Karte

- [ ] stilisierte 0–100-Koordinaten in echte responsive Kartenfläche umsetzen
- [ ] Bezirksflächen mit Heat/Prestige/Polizeidruck/Szeneaktivität sichtbar machen
- [ ] 12 Orte mit Kategorie, Score und Tier darstellen
- [ ] Eigentum und Ausbauzustand klar markieren
- [ ] Hall of Tribute als besonderen Prestige-Ort hervorheben
- [ ] keine reale Navigations-/Adresskarte vortäuschen

### C3 – Interaktion

- [ ] Klick/Fokus auf Bezirk → bestätigte Bezirkswerte und letzte Änderung zeigen
- [ ] Klick/Fokus auf Location → Basiswerte, effektive Ausbauwerte, Score/Tier und Eigentum zeigen
- [ ] Property-Kauf/-Ausbau weiterhin ausschließlich über vorhandene A4-Commands delegieren
- [ ] Tastatursteuerung und sichtbaren Fokus sicherstellen
- [ ] Reduced-Motion-Variante ohne Informationsverlust

### C4 – Robustheit / Abnahme

- [ ] Projection-Tests für Wert-/Tier-/Ownership-Darstellung
- [ ] Responsive- und Accessibility-Vertrag testen
- [ ] prüfen, dass Renderer keine Domainwerte berechnet oder persistiert
- [ ] A4 First Run und Release Package unverändert grün halten
- [ ] Runtime Core ✅
- [ ] Presentation Core ✅
- [ ] Repository Health ✅
- [ ] Release Acceptance ✅
- [ ] Release Package ✅
- [ ] 0 Review-Threads
- [ ] `/safe-merge`

### Explizit NICHT in 0.8.6-C

- keine neuen District-Regeln
- keine neuen Property-Kosten
- keine Miete, Rendite oder Verkauf
- keine neue Event-Bonuslogik
- kein Netzwerk-/Telegram-State
- keine echte Navigation oder Geocoding-Abhängigkeit

---

# Danach – priorisierter Ausbau

1. **0.8.7-A – Saisonale Hall of Tribute:** bestätigter Wochen-/Monatszyklus mit Prestige-Titeln; Zeitautorität separat härten.
2. **0.8.7-B – Bezirksbezogene Welt-Ereignisse:** DistrictState als echte Quelle, reproduzierbare Ereignisinstanzen.
3. **0.9 – Network Foundation:** erst nach eigenem Server-/Transport-/Konfliktvertrag; niemals UI- oder Telegramdaten direkt als Domainautorität.

---

## Arbeitsregeln

- Pro Iteration kleinster sinnvoller Scope.
- Keine zweite Implementierung eines bereits vorhandenen Services/States.
- UI/Renderer schreibt Domain-State niemals direkt.
- Economy nur über kanonische Economy-Services/Events.
- Journal bleibt append-only.
- Systemzeit ist niemals alleinige Zufalls- oder Saisonautorität.
- Normaler Merge ausschließlich nach aktuellem `main`, grünen Required Checks, 0 offenen Review-Threads und `/safe-merge`.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
