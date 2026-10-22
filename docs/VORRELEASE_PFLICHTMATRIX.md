# BUNKERFREQUENZ – Vorrelease-Pflichtmatrix

Stand: 21.10.2026. Ausgangs-HEAD: `15b440c974acb3bc594d2d4c8e7ecd3f53d28c31`.

Diese Matrix ist eine Entwicklungsplanung, keine Freigabe. Ein PASS erfordert den tatsächlich geprüften Commit und die dazugehörige CI-Run-ID.

| Pflicht | Prüfquelle | Status |
|---|---|---|
| Spiellogik und vollständige Eventpartie | `tests/runtime/test_a4_first_run_smoke.py` | Neue Gesamtabnahme offen |
| Charakter, Jobs, Bank, Handel, Immobilien, Bezirke und Ranking | `TODO.md`, `FEATURE_POOL.md` | Funktionen dokumentiert; Regression offen |
| Speicherung, Journal, Snapshot, Neustart und Recovery | `docs/PERSISTENCE_CONTRACT.md` | Neue Gesamtabnahme offen |
| Sicherheit, Startbarkeit und Belastung | `docs/RELEASE_ACCEPTANCE_0.8.4.md` | Neue Gesamtabnahme offen |
| Layout 800×600, 200 % Skalierung, Kontrast, Tastatur | `tools/desktop_browser_e2e_pro.py` | Vollständiger Nachweis offen |
| Paket, SHA-256, Wiederherstellung und Release-Unterlagen | `docs/RELEASE_AUTOPILOT_PRO.md` | Neue Gesamtabnahme offen |
| Main-Integrität und Status-Sync | `.github/workflows/` | Rote Checks auf Ausgangs-HEAD; zu klären |
| Nutzer-Sichtprüfung und Kubuntu-Praxistest | Einmaliges finales Release-Gate | Ausschließlich unmittelbar vor Release |

Nächster technischer Schritt: Release-Prüfung gegen leere oder unbekannte Gate-Zustände absichern. Kein Release, kein ungeprüfter Merge und keine Nutzer-Zwischenabnahme.

## Funktionsinventar und offene Nachweise

Die folgende Aufteilung ist aus README, TODO, FEATURE_POOL, Status und den bestehenden Verträgen abgeleitet. „Bestand“ heißt nur: Code/Vertrag oder ältere Nachweise sind vorhanden. **Keine dieser Zeilen ist ein neuer PASS auf dem aktuellen HEAD.**

| ID | Vorgesehenes Spielelement | Vertrags- oder Testanker | Zustand |
|---|---|---|---|
| 01 | Crew, Charakterprofil, Avatar, Skills, Traits, Level und Ressourcen | `docs/CHARACTER_FORGE.md`, `docs/PROGRESSION_CONTRACT.md` | Bestand; Gesamttest offen |
| 02 | Straßenbegegnungen mit vier Ansätzen, Zufallsgewichten und Grenzwerten | `manifests/STREET_ENCOUNTER_MANIFEST.json`, `tests/gameplay/` | Bestand; Replay offen |
| 03 | Fünf Jobs, Energie-/Stresskosten und reduzierter Lohn | `docs/ARBEIT_GELD_HANDEL_LAIENHILFE.md` | Bestand; Grenzwerte offen |
| 04 | Bargeld, Bank, Sparzins und Kontoauszug TXT/CSV | `docs/ECONOMY_0.8.2.md` | Bestand; Langzeit-/Rundungstest offen |
| 05 | Equipmentkauf, Verkauf, Reservierung, Freigabe, Historie | `docs/EQUIPMENT_TRADE_HISTORY_AUDIT.md` | Bestand; Bestands-/Ledgerprüfung offen |
| 06 | Immobilien, Eigentum, Ausbau Level 1–3 und Ortswerte | `manifests/PROPERTY_MANIFEST.json` | Bestand; Wiederherstellung offen |
| 07 | Eventplanung, Beschaffung, Transport, Aufbau, Soundcheck, Live, Abbau, Abschluss | `tests/runtime/test_a4_first_run_smoke.py` | Bestand; neue Langzeitpartien offen |
| 08 | Krisen, Reaktionen, Folgen, Abrechnung mit/ohne Krise | `docs/CRISIS_CITY_0.8.3-B.md`, `docs/SETTLEMENT_0.8.3-C.md` | Bestand; Alternativpfade offen |
| 09 | Bezirksereignisse, Nachhallketten, Spielweltzeit, genau einmalige Wirkung | `docs/DISTRICT_CHAIN_CONTRACT_V1.md` | Bestand; Recovery-/Zeitgrenzen offen |
| 10 | Berlin-Karte, acht Bezirke, zwölf Orte, Crew-Ranking, Hall of Tribute | `docs/SPIELBESCHREIBUNG_TECHNISCH.md` | Bestand; Anzeige-/Datenprüfung offen |
| 11 | Venue-Betriebsprofil, ausschließlich eigene Orte und bestätigte Werte | `docs/VENUE_OPERATING_PROFILE_PRESENTATION_CONTRACT.md` | PR #278 aktiv; nicht parallel ändern |
| 12 | Einfache erste Partie, lokale Oberfläche, Hilfen und Fehlermeldungen | `docs/A4_FIRST_RUN_ANLEITUNG.md` | Bestand; End-to-End offen |

## Qualitäts- und Release-Pflichten

| ID | Prüffeld | Prüfweg | Status |
|---|---|---|---|
| Q01 | Save, Journal, Snapshot, Neustart, beschädigte Daten, Legacy-Saves | `docs/PERSISTENCE_CONTRACT.md`, `tests/runtime/` | Offen auf Ziel-HEAD |
| Q02 | Offline-Start, Portkollision, Pfadschutz, localhost, fremde Schreib-Origins | `tests/release/test_a4_release_acceptance.py` | Offen auf Ziel-HEAD |
| Q03 | Absturz, ENOSPC, Prozessgrenzen, Speicherlast und lange Pfade | `tools/failure_containment_pro.py` | Offen auf Ziel-HEAD |
| Q04 | 800×600, 175–200 % Skalierung, lange Texte, kein horizontales Überlaufen | `tools/start_a4_acceptance.py`, `tools/desktop_browser_e2e_pro.py` | Echter Chromium-PASS bei 800×600/großer Schrift ohne Seitenüberlauf (Run 39666775754). 175–200 % Browserzoom und Vollansichten weiterhin offen. |
| Q05 | Tastatur, Fokus, Kontrast, große Schrift, reduzierte Animation | `tests/presentation/`, `docs/UI_UX_BLUEPRINT.md` | Sichtbarkeit/Fokussierbarkeit von Sprunglink und Ansichtsknopf im echten Chromium geprüft. Echte Tab-Navigation und Kontrast-Gesamttest noch offen. |
| Q06 | Chromium und Firefox: Hauptspielschleife, keine Hänger | `tools/desktop_browser_e2e_pro.py` | Neuer Quellstand offen |
| Q07 | Linux-Klickstart und entpacktes Paket ohne Entwicklerumgebung | `START_BUNKERFREQUENZ.sh`, `tests/release/` | Neuer Quellstand offen |
| Q08 | Bytegleiches Paket, SHA-256, Dateimodi, unveränderte Quellen | `tools/release_autopilot.py` | Neuer Quellstand offen |
| Q09 | Fehlende/ungültige Prüfergebnisse dürfen keine Freigabe ergeben | `evaluate_release_state` | Auf PR #279 behoben; Negativtests und CI am geprüften Stand PASS |
| Q10 | Drei Required Checks, Review-Threads, Safe-Merge, Main Integrity | `.github/workflows/` | **Blockiert: Main Integrity rot** |
| Q11 | Statusdateien konsistent und mit echten Nachweisen | `tools/status_sync.py` | PR #279: kanonische Anker auf bestätigten PR #276 gebracht; Status-Sync PASS (Run 39666775031). Nicht mit Main-Integrity-Vorfall verwechseln. |
| Q12 | Versions-Freeze, Changelog, Release Notes, Rückfall, Evidence-Chain | `VERSION.json`, `CHANGELOG.md`, `docs/RELEASE_EVIDENCE_CHAIN_PRO.md` | Offen |
| Q13 | Einmalige persönliche Sicht-/Kubuntu-/Spielgefühl-Endabnahme | Release-Kandidat | **Ganz zuletzt**, kein Zwischentest |

**Gezielte Ursachenprüfung (GitHub-Fehllogs, 25.09.2026):** Main Integrity beanstandet `15b440c974ac` ausdrücklich als **keinen Zwei-Eltern-PR-Merge** (Direkt-/Rebase-/Squash-Push). Status Sync erwartet nach dem letzten relevanten Safe-Merge **PR #276 / `0d3122532e639bc347cd75db11e9f94aaa0e7a27`**, während `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json` noch auf **PR #273 / `ad3b64d67200be639260159c675048cde21ccb8f`** zeigen. Das sind getrennte Blocker; keine Umschreibung von `main`, kein künstlich grünes Gate.

**Rote Ist-Nachweise:** Auf `main`-Commit `15b440c974acb3bc594d2d4c8e7ecd3f53d28c31` meldet GitHub für Main Integrity Run `36186414235` und Status Sync Run `36186414155` `failure`; Issue #277 ist offen. Ursache zuerst anhand der konkreten Fehljobs klären, keine Schutzregel umgehen.

**Sicherer nächster Arbeitsschritt:** Den leeren bzw. unbekannten Gate-Zustand im Release Autopilot als ungültig behandeln und durch Negativtests belegen. Danach Main-Integrität und Status-Sync gezielt untersuchen; 800×600/200%- und Tastatur-Browsertests ergänzen. Alles auf demselben eingefrorenen Commit nachweisen. Keine persönlichen Nutzer-Zwischenabnahmen.

**Laiensicht:** „Das Programm wurde gebaut“ ist nicht dasselbe wie „Das Spiel ist fertig geprüft“. Erst die vollständigen grünen Nachweise machen es zum Vorrelease-Kandidaten. Deine persönliche Gesamtprüfung findet **einmal ganz am Ende** statt.

**Spätere Verbesserungsidee:** Eine bestehende Repository-Health-Prüfung könnte diese Matrix automatisch mit den konkreten Run-IDs und SHAs abgleichen, ohne eine zweite Freigabeengine aufzubauen.

## Ausführungsnachweis 21.10.2026

- Entwicklungszweig: `fix/release-gate-fail-closed-prerelease-matrix-20261021`, ausschließlich vom damaligen `main`-HEAD abgezweigt; `main` unverändert.
- `evaluate_release_state` gegen leere, fehlerhafte und unbekannte Gate-Einträge abgesichert; zugehörige Unit-Regression ergänzt.
- **Isolierte Funktionsprüfung:** 9 Fälle unter Python 3 erfolgreich. Das ist **kein** vollständiger Repository-/CI-Nachweis.
- **BLOCKED:** Die GitHub-Schnittstelle verweigerte die PR-Erstellung mehrfach. Daher kein PR, keine PR-gebundenen Required Checks und keine Merge-Freigabe. Kein Versuch, Schutzregeln zu umgehen.
- Vergleichsseite: `https://github.com/provoware/game_more_core/compare/main...fix/release-gate-fail-closed-prerelease-matrix-20261021`.
- Die fachliche Änderung bleibt vorläufig im separaten Entwicklungszweig; die offenen CI- und Integritätsprüfungen sind **nicht** als PASS markiert.

## Nachtrag – GitHub PR #279 (21.10.2026)

- **PR:** https://github.com/provoware/game_more_core/pull/279 (Entwicklungszweig, `main` unverändert).
- **Status-Sync:** Die ursprüngliche fehlerhafte CI benannte exakt PR #273 statt des nachgewiesenen letzten relevanten Safe-Merges **PR #276** (`0d3122532e639bc347cd75db11e9f94aaa0e7a27`). `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json` sind auf dem PR-Zweig korrigiert. Die dynamische Git-Historienprüfung bleibt unverändert; zwei veraltete, fest auf #273 verdrahtete Runtime-Tests wurden auf Dateikonsistenz umgestellt. **PASS:** https://github.com/provoware/game_more_core/actions/runs/39666080006 (Runtime), https://github.com/provoware/game_more_core/actions/runs/39666775031 (Status Sync).
- **Echter Chromium-Nachweis:** Der vorhandene Avatar-Context-E2E misst nach dem bisherigen 760×680-Test nun zusätzlich eine **800×600**-Ansicht mit großer Schrift, horizontalem Seitenüberlauf sowie sichtbarem Fokus von Sprunglink und Ansichtsknopf. Ein anfänglicher fehlerhafter Vergleich mit der Scrollleisten-bereinigten Breite wurde korrigiert; **PASS:** https://github.com/provoware/game_more_core/actions/runs/39666775754 (Commit `4bd6a2b532a3b35b12202f11d81b865f6242adde`). **Grenze:** programmatischer Fokus ist noch kein nativer Tab-Tastaturtest und „große Schrift“ entspricht keiner bestätigten 175–200-%-Browser-Zoomprüfung.
- **Historischer Main-Integrity-Vorfall #277:** https://github.com/provoware/game_more_core/issues/277. Exakter Fehler: Commit `15b440c974acb3bc594d2d4c8e7ecd3f53d28c31` in `main` ist kein zweielterlicher Safe-Merge, unabhängig davon, ob ein neuer PR grün wird. **Offen:** Berechtigungs-/Provenienz-Audit und künftige Safe-Merge-Regel sicherstellen. Kein Force-Push, keine Umschreibung, keine vorgetäuschte historische Freigabe.
- **Nächste Pflicht:** eigene Browser-QA für echtes 175–200-%-Zoom, native Tastatur-Tabfolge und weitere Spielansichten, danach erneute Gesamtprüfkette mit endgültigem SHA. Nutzer-Endabnahme ausschließlich unmittelbar vor Release.
