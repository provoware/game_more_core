# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – weiterhin letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.6-C – Berlin Ops Map PRO`
- **0.8.6-A Property Purchase:** PR #82 · Merge `192b3eb4ad9dc4272eafeddc8604f7265bdd30fa`
- **0.8.6-B Property Upgrades:** PR #83 · Merge `0b301bc9004f60dbc3ce221a7c6b3e462766b5b7`
- **0.8.6-C Berlin Ops Map PRO:** PR #85 · Head `6c302ce9425b27e7a1175a1cdcf463a100fc7191` · Runtime `32592128107` · Presentation `32592128117` · Repository Health `32592128103` · Release Acceptance `32592128147` · Release Package `32592128113` · 0 Review-Threads · `SAFE MERGE PASS` · Merge `10c7d6b5e04838b07ae6899b8b76580cd87de607`
- **Erstes lokales Alpha:** `0.8.4-alpha.1` · ZIP SHA-256 `fccf16ee3728827ba4eba0dfd0e3cbaf844dd68c382b3c29c766f94a7ef85146`
- **Nächster Pflichtblock:** `0.8.7-A – Saisonale Hall of Tribute`
- **Release-Blocker:** keiner für `0.8.4-alpha.1`; ein neuer Produktrelease benötigt weiterhin eine eigene Release-Abnahme

---

# Abgeschlossen ✅

## 0.8.1–0.8.5 – Kernspiel und Living World

- [x] Character Forge, Skills, Traits und Progression
- [x] Event State + Equipment/Economy
- [x] Event Execution + Crisis/Incident + Settlement
- [x] schreibender lokaler A4-Client mit Save/Snapshot/Recovery
- [x] Competitive Ranking, Profilpersonalisierung und Street Encounters
- [x] persistente Living Districts
- [x] Hall of Tribute / sichtbare Top 10

## 0.8.6-A – Property Purchase Foundation ✅

- [x] 7 kaufbare Berlin-Ops-Orte über kanonische Economy autorisieren
- [x] Client besitzt keine Preis-/Owner-/Budgetautorität
- [x] Economy + Event-Budget + PropertyState atomar bestätigen
- [x] `world.property_purchased` append-only journalisieren
- [x] Combined Recovery, Idempotenz, Fault-Injection und Manipulationsschutz
- [x] PR #82 sicher gemergt

## 0.8.6-B – Property Upgrades ✅

- [x] separater rückwärtskompatibler `PropertyUpgradeState`
- [x] 10 Ausbauarten, Level 1–3, feste Kostenleiter
- [x] Client besitzt keine Kosten-/Level-/Deltaautorität
- [x] Economy + Event-Budget + Upgrade-State atomar bestätigen
- [x] `world.property_upgraded` + Combined Recovery
- [x] effektive Standortwerte → bestehender City-Map-Score/Tier
- [x] PR #83 5/5 grün und sicher gemergt

## 0.8.6-C – Berlin Ops Map PRO ✅

- [x] `BERLIN_OPS_MAP_PRO_MANIFEST.json` als read-only Presentation-Vertrag
- [x] vorhandene Living-District-/City-Map-/Property-/Upgrade-Projections als einzige Datenquellen
- [x] 8 District-Flächen und 12 Locations auf stilisierten 0–100-Koordinaten
- [x] District-Werte Heat, Prestige, Polizeidruck und Szeneaktivität sichtbar
- [x] Location-Details mit Score, Tier, Rang, Eigentum, Standortwerten und Ausbaulevel
- [x] reine Sichtfilter `all / owned / prime / hall`
- [x] Tier, Eigentum und Hall auch ohne reine Farbcodierung unterscheidbar
- [x] Tastaturfokus, ARIA, sichtbarer Fokus und Reduced Motion
- [x] `map_pro.js` ohne `/api/command`, `fetch()`, Geolocation oder externe Kartendienste
- [x] Launcher-Preflight verlangt Manifest + Rendererdatei
- [x] Projection-/Fail-Closed-/Browser-Vertrag regressionsgedeckt
- [x] Runtime Core `32592128107` ✅
- [x] Presentation Core `32592128117` ✅
- [x] Repository Health `32592128103` ✅
- [x] Release Acceptance `32592128147` ✅
- [x] Release Package `32592128113` ✅
- [x] 0 Review-Threads
- [x] `/safe-merge` PASS · Merge `10c7d6b5e04838b07ae6899b8b76580cd87de607`

---

# AKTIV / NÄCHSTER PFLICHTBLOCK

## 0.8.7-A – Saisonale Hall of Tribute 🏆

### Ziel

Die bestehende Hall erweitert sich um **bestätigte Wochen-/Monatszyklen**, ohne lokale Gegner, Ergebnisse oder Zeitgrenzen zu erfinden. Die Systemzeit darf niemals alleinige Saisonautorität sein.

### A1 – Zeit- und Saisonvertrag

- [ ] vorhandene Zeit-/Ranking-Verträge zuerst auf Wiederverwendung prüfen
- [ ] bestätigte `cycle_id`/Zyklusmetadaten als Autorität definieren
- [ ] Wochen- und Monatszyklen klar trennen
- [ ] Systemzeit nur als Anzeige-/Plausibilitätswert zulassen, nicht als alleinige Autorität
- [ ] Replay desselben bestätigten Zyklus deterministisch halten

### A2 – Saisonale Ranking-Projection

- [ ] bestehende Competitive-Ranking-Engine wiederverwenden
- [ ] lokale Hall erfindet weiterhin keine Remote-Teilnehmer
- [ ] aktuelle und abgeschlossene Zyklen unterscheidbar projizieren
- [ ] Titel ausschließlich aus bestätigtem Zyklus + bestätigtem Ranking ableiten
- [ ] mögliche Titel katalogisieren, z. B. Lärmadel, Bunkerbaron, Kabelkönig, Pegelpapst, Nachtminister

### A3 – A4-Hall-Darstellung

- [ ] Wochen-/Monatsansicht ohne zweite Sortierlogik im Browser
- [ ] Zyklusstatus und bestätigten Titel sichtbar machen
- [ ] bestehende Ruf-/Level-/Resonanzansichten erhalten
- [ ] Tastatur-/Reduced-Motion-Verträge beibehalten

### A4 – Robustheit / Abnahme

- [ ] Zyklus-ID-, Replay- und Boundary-Regressionen
- [ ] keine Zeit-Rerolls durch Reload
- [ ] keine erfundenen Teilnehmer/Titel
- [ ] bestehende Hall-/Map-/Property-Funktionen regressionsfrei
- [ ] Runtime Core
- [ ] Presentation Core
- [ ] Repository Health
- [ ] Release Acceptance
- [ ] Release Package
- [ ] 0 Review-Threads
- [ ] `/safe-merge`

### Explizit NICHT in 0.8.7-A

- kein Telegram-/Server-Sync
- keine echten Netzwerkgegner ohne bestätigte Netzwerkdaten
- keine neue globale Zeitengine ohne Bedarf
- keine District-Zufallsereignisse
- keine Property-Boni oder laufenden Einnahmen

---

# Danach – priorisierter Ausbau

1. **0.8.7-B – Bezirksbezogene Welt-Ereignisse:** DistrictState als Quelle, reproduzierbare Ereignisinstanzen.
2. **0.8.7-C – Street Encounter Content Packs:** mehr Vielfalt über denselben validierten Encounter-Vertrag.
3. **0.9 – Network Foundation:** eigener Server-/Transport-/Konfliktvertrag vor Telegram-/Ranking-Sync.

---

## Arbeitsregeln

- Pro Iteration kleinster sinnvoller Scope.
- Keine zweite Implementierung eines vorhandenen Services/States.
- UI/Renderer schreibt Domain-State niemals direkt.
- Economy nur über kanonische Economy-Services/Events.
- Journal bleibt append-only.
- Systemzeit ist niemals alleinige Zufalls-, Saison- oder Replayautorität.
- Normaler Merge ausschließlich nach aktuellem `main`, grünen Required Checks, 0 offenen Review-Threads und `/safe-merge`.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
