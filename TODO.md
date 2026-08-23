# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.7-B – Control Deck & Player Choices` · PR #88 · Merge `4d1a35bfbc086d07599b6ec7b3816e830bcea995`
- **0.8.7-C1 District-Event-Vertrag/Katalog:** PR #90 · `SAFE MERGE PASS` · Merge `337f8ad8f9719ec3389c372da9688bbbec593c16`; kanonischer Feature-Status wird erst in eigener Statuspflege weitergezogen
- **Aktive Iteration:** `0.8.7-C2 – District-Event Runtime`; deterministische Auswahl + bestätigte District-Anwendung, noch ohne A4-Auslösung
- **Release-Blocker:** keiner für `0.8.4-alpha.1`; ein neuer Produktrelease benötigt weiterhin eine eigene Release-Abnahme

---

# Abgeschlossen ✅

## 0.8.1–0.8.6 – Kernspiel, Living World, Property & Map

- [x] Character Forge, Event-State, Economy, Crisis und Settlement
- [x] schreibender lokaler A4-Client mit Save/Snapshot/Recovery
- [x] Competitive Ranking, Profilpersonalisierung und replaybare Street Encounters
- [x] persistente Living Districts
- [x] Property Purchase + Property Upgrades
- [x] Berlin Ops Map PRO mit 8 Districts, 12 Locations, Eigentum/Ausbau und read-only Filtern

## 0.8.7-A – Saisonale Hall of Tribute ✅

- [x] Wochen- und Monatszyklen mit explizitem Saisonvertrag
- [x] bestehende Competitive-Ranking-Engine wiederverwendet
- [x] `game_world_time` aus abgeschlossenem bestätigtem Event als stabiler lokaler Anker
- [x] Systemzeit niemals alleinige Saisonautorität
- [x] endgültige Titel nur bei geschlossenem bestätigtem Zyklus + echter bestätigter Konkurrenz
- [x] lokale Einzelspieler-Hall vergibt keine Fake-Championtitel
- [x] Wochen-/Monatssicht im A4-Client
- [x] `/safe-merge` PASS · Merge `841258a37915e05d7f87eed7841c8e4b8d79bf46`

## 0.8.7-B – Control Deck & Player Choices ✅

- [x] Sticky HUD und Schnellnavigation
- [x] Kompaktmodus, hoher Kontrast und große Schrift ausschließlich lokal
- [x] vier Street Approaches mit katalogisierten Auswahlgewichten
- [x] Encounter bleibt einzige Effekt-Autorität
- [x] Krisenentscheidungen zeigen katalogisierte Folgen vor dem Klick
- [x] Browser sendet weiterhin nur erlaubte IDs
- [x] `/safe-merge` PASS · Merge `4d1a35bfbc086d07599b6ec7b3816e830bcea995`

## 0.8.7-C1 – District-Event-Vertrag/Katalog ✅

- [x] vorhandenen DistrictState-Vertrag als einzige Metrik-/Bounds-Basis referenzieren
- [x] vier Ereignisse mit stabilen IDs, Gewichten, Voraussetzungen und kleinen Effekten definieren
- [x] Auswahlvertrag deterministisch/replaybar halten; Systemzeit nie als Seed
- [x] Browser-Aktivierung und Browser-Effektwerte ausdrücklich verbieten
- [x] deutsche Story-Texte separat von Spiellogik katalogisieren
- [x] gezielte Vertragsregressionen ergänzen
- [x] `/safe-merge` PASS · Merge `337f8ad8f9719ec3389c372da9688bbbec593c16`

---

# AKTIVER AUSBAU

## 0.8.7-C2 – District-Event Runtime

### Ziel

Der C1-Katalog wird über eine kleine deterministische Runtime ausführbar, ohne zweite District-Engine oder Browser-Autorität.

- [x] Auswahlservice aus bestätigtem `world_seed + district_id + trigger_id` implementieren
- [x] Voraussetzungen vor der gewichteten Auswahl gegen aktuellen DistrictState prüfen
- [x] bestätigte Folgen über den vorhandenen `DistrictService` und `world.district_effect_applied` journalisieren
- [x] derselbe District-/Trigger-Kontext darf auch bei verändertem Retry-Seed nicht erneut würfeln oder doppelt anwenden
- [x] vorhandenen District-Recovery-Pfad für den resultierenden Journalrecord regressiv absichern
- [x] ungültigen District-Kontext vor jedem Write ablehnen
- [ ] Runtime aus einem kanonischen Game-Client/Application-Flow auslösen; Browser sendet dabei keine Effekte
- [ ] District-Event read-only in Projection/A4 sichtbar machen

### Explizit NICHT in C2

- keine neue Journal-Eventart
- keine zweite Crisis-/Street-Engine
- keine JavaScript-District-Regeln
- keine Netzwerkgegner
- kein Property-Resale/Rent-System
- kein Produktversionsbump ohne eigene Release-Abnahme

---

# Danach – priorisierter Ausbau

1. **0.8.7-C3 – Application-Integration:** autorisierten Trigger in den bestehenden Spielablauf einhängen, ohne Client-Effektwerte.
2. **0.8.7-C4 – Ereignis-Timeline:** bestätigte District-, Street- und Crisis-Ereignisse read-only im Control Deck zeigen.
3. **0.8.7-D – Street Content Packs:** mehr Abwechslung über denselben validierten Ansatz-/Encounter-Vertrag.

---

## Arbeitsregeln

- Pro Iteration kleinster sinnvoller Scope.
- Keine zweite Implementierung vorhandener Services/States.
- UI/Renderer schreibt Domain-State niemals direkt.
- Economy nur über kanonische Economy-Services/Events.
- Journal bleibt append-only.
- Systemzeit ist niemals alleinige Zufalls-, Saison- oder Replayautorität.
- Normaler Merge ausschließlich nach aktuellem `main`, grünen Required Checks, 0 offenen Review-Threads und `/safe-merge`.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
