# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.7-C5 – District-Event Cadence/Cooldown` · PR #102 · Merge `bd79da8d1e124ec60248a05bf332c6ef338ca7b6`
- **0.8.7-C4B sichtbare Timeline:** PR #101 · 5/5 Gates · `SAFE MERGE PASS` · Merge `3d71f00c5717ae797e6b8f1ca4c65c036bf71c81`
- **0.8.7-C5 Cadence/Cooldown:** PR #102 · 5/5 Gates · `SAFE MERGE PASS` · Merge `bd79da8d1e124ec60248a05bf332c6ef338ca7b6`
- **District-Event-Taktung:** global 24 bestätigte Spielweltstunden; Autorität `event.time_window.start_local`; keine Systemzeit-Freigabe
- **Aktive Entwicklungsstufe:** `0.8.8-A – Crew Identity Foundation`
- **Release-Blocker:** keiner für `0.8.4-alpha.1`; neuer Produktrelease benötigt eigene Release-Abnahme

---

# Abgeschlossen ✅

## 0.8.7-C – District World Events & Timeline

- [x] C1: stabiler District-Event-Katalog mit deterministischer Auswahl
- [x] C2: Runtime, Journal-/Recovery-Nutzung, Fail-fast-Katalogprüfung
- [x] C3: ausschließlich `settlement.complete` als autorisierter Application-Trigger
- [x] C4A: read-only Timeline-Projection aus bestätigten Journalrecords
- [x] C4B: Timeline im Control Deck sichtbar, Browser sortiert oder schreibt nichts
- [x] C5: 24h-Cadence aus bestätigter Spielweltzeit; Retry/Reload bleibt idempotent
- [x] `no_eligible_event`, fehlende bestätigte Zeit und aktiver Cooldown bleiben schreibfreie No-ops
- [x] C4B Remote-Abnahme: Runtime `32644333670`, Presentation `32644333674`, Repository Health `32644333688`, Release Acceptance `32644333694`, Release Package `32644333686`
- [x] C5 Remote-Abnahme: Runtime `32646269065`, Presentation `32646269053`, Repository Health `32646269009`, Release Acceptance `32646269064`, Release Package `32646269010`

---

# Aktiv – 0.8.8-A Crew Identity Foundation

## Ziel

Jeder Spieler erhält eine eigene Crew-Identität als **Logo oder Fahne**, die später ohne Bilddatei-Konflikte synchronisierbar ist.

- [ ] kanonischen Crew-Identity-Vertrag als kleine Datenrepräsentation definieren: Stil, Symbol, Primär-/Sekundärfarbe, Akzent, optionale Kurzmarke
- [ ] keine frei eingebetteten Base64-/Datei-Bildblobs im Character-State; Renderer erzeugt Logo/Fahne aus bestätigten Daten
- [ ] Profiländerung ausschließlich über bestehenden `profile.update`-Pfad
- [ ] Character-ID und Gameplaywerte bleiben unverändert
- [ ] Projection/Control Deck zeigt die bestätigte Crew-Identität
- [ ] zukünftiger Sync-Vertrag muss Crew-Identity-Daten bei allen bestätigten Spielern nachziehen können
- [ ] Legacy-Saves ohne Crew-Identity erhalten einen stabilen neutralen Default, ohne Journal-Umschreibung
- [ ] Runtime-, Presentation- und Recovery-Regressionen ergänzen

---

# Priorisierter Ausbau nach 0.8.8-A

1. **0.8.8-B – Scene Jobs & Sparschleife:** jederzeit verfügbare legale/szenetypische Jobs mit klaren Zeit-/Energie-/Stress-/Geldfolgen; vorhandene Economy-Persistenz wiederverwenden.
2. **0.8.8-C – Secret Best Friend Assistant:** genau eine Aufgabe aktiv; Assistent führt sie pro bestätigter Runde wiederholt aus, bis der Spieler deaktiviert oder umstellt; keine Hintergrund-Systemzeit.
3. **0.8.8-D – Bank & Investments:** Bargeld einzahlen/abheben, Sparzins, Zinseszins, Anlagen/Dividenden und nachvollziehbare Kontoauszüge; alles journalisiert und replaybar.
4. **0.8.8-E – Control Deck Focus:** Informationen verdichten, doppelte Ansichten entfernen, jeden Arbeitsbereich lokal maximieren/zurücksetzen, nächste erlaubte Aktion deutlich hervorheben; Reduced Motion respektieren.
5. **0.8.8-F – Berlin Ops Map 2:** bezirksartige Darstellung, Zoom/Pan, bessere Objekt-Hierarchie und Detailansicht; Karte bleibt read-only.
6. **POOL-STORY-001 – Ereignis-Nachhall:** bestätigte wichtige District-Ereignisse später in der Crew-Biografie aufgreifen.
7. **POOL-UX-003 – Timeline-Fokusfilter:** lokal Straße/Krise/Bezirk filtern, ohne Reihenfolge oder Save-State zu verändern.

---

## Architektur- und Sicherheitsgrenzen für den Ausbau

- Keine Mega-PR: pro fachlichem Modul eigener kleiner Slice.
- Keine zweite Economy-, Map-, Timeline-, Profile- oder Sync-Engine.
- Browser sendet nur erlaubte IDs/Darstellungswerte; Geld, Effekte, Zinsen, Dividenden und Assistentenfolgen werden serverseitig bestimmt.
- Wiederholte Assistentenaktionen und Finanzzyklen brauchen bestätigte Spielrunde/Spielweltzeit; niemals Systemzeit allein.
- Blink-/Puls-Hinweise sind reine lokale Presentation, dürfen Gameplay nicht blockieren und müssen bei Reduced Motion statisch werden.
- Map-Zoom, Focus-Maximierung und Timeline-Filter sind lokale UI-Zustände und gehören nicht ins Journal.
- Crew-Logo/Fahne wird als kleine kanonische Identitätsdaten synchronisiert, nicht als unkontrollierter Bildblob.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
