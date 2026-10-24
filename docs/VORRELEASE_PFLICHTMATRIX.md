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

## 24.10.2026 – Q01: Checkpoint- und Metadatenstruktur (separater Entwicklungszweig)

**Ziel:** Beschädigte, aber syntaktisch gültige JSON-Spielstände und Save-Metadaten dürfen weder ungefangene Typfehler noch stille Datenübernahme verursachen. **Abnahme:** ungültige Objektformen werden als `PersistenceError` kontrolliert abgewiesen; mit gültigem Snapshot gelingt Recovery ohne Verlust des gespeicherten Zustands; ohne gültigen Checkpoint bleiben Quelldateien bytegleich und Recovery verweigert den Eingriff.

| Soll / Pflicht | Ist / Beleg | Status |
|---|---|---|
| Q01: State-Envelope mit Objekt, Schema, ganzzahliger Sequenz, Hash und Objekt-Daten | `src/bunkerfrequenz/infrastructure/persistence.py`; `tests/runtime/test_persistence_checkpoint_shape.py` | PASS für diesen Teilschutz auf `2bb2fa12a99c0a22a53081f5bc82571c81422777`; finaler Dokumentations-HEAD erneut zu prüfen |
| Q01: Save-Metadaten mit Objekt, Sequenz und Journal-Hash | dieselben Dateien; boolesche und fehlerhafte Werte werden abgelehnt | PASS für diesen Teilschutz auf `2bb2fa12a99c0a22a53081f5bc82571c81422777`; finaler HEAD erneut zu prüfen |
| Q01: Snapshot-Fallback bei beschädigtem State/Meta | temporäre Saves und echter `PersistenceKernel.recover` in neuen Regressionen | PASS im `runtime-core` auf `2bb2fa12a99c0a22a53081f5bc82571c81422777`; finaler HEAD erneut zu prüfen |
| Q01: Kein gültiger Checkpoint ⇒ kein Überschreiben | Bytevergleich vor/nach verweigerter Recovery | TEST VORGESEHEN – CI-Nachweis erforderlich |
| Q01: Stromausfall, Dateisystem-Fehler, Langzeitpartie, Legacy-Migration | separate End-to-End- und Fehlermatrix noch nötig | OFFEN |
| Q04–Q13: UI, Performance, Integrität, Release, persönliche Endabnahme | andere Pflichtpakete / historische Integritätsvorfälle #277 und #280 | OFFEN / BLOCKED; persönliche Abnahme zuletzt |

**Geplante Prüfung:** `PYTHONPATH=src python3 -m unittest tests.runtime.test_persistence_checkpoint_shape -v`, vollständiges `runtime-core`-Gate, danach sämtliche PR-Gates auf exakt dem letzten SHA. Status `PASS` erst nach echten Nachweisen; kein Merge, kein Release.

**Abgrenzung:** Kein bestehender Spielstand wird geöffnet oder verändert. Keine neue Recovery-Engine, kein neues Save-Format, keine Änderungen an Journal/Gameplay/Map. Die frühere Legacy-Objektform bleibt zulässig, solange die zugehörigen Metadaten gültig sind. Der Entwicklungszweig ist unabhängig von Karten-PR #282.

**Nächste technische Pflicht:** Journal- und Snapshot-Fehlerpfade mit simulierten Unterbrechungen und echten Event-Replays über die vollständige Spielschleife prüfen; dabei auch fehlerhafte Metadaten nach einem bestätigten Journalereignis abdecken. Erst anschließend Langzeitpartien und Release-Evidence-Chain.

**Remote-Prüfung auf Implementierungs-HEAD `2bb2fa12a99c0a22a53081f5bc82571c81422777` (24.10.2026):**
- Runtime Core: **PASS**, [Run #40070628591](https://github.com/provoware/game_more_core/actions/runs/40070628591), einschließlich der drei neuen Testmethoden mit 20 strukturell ungültigen State-/Meta-Varianten.
- Presentation Core: **PASS**, [Run #40070628605](https://github.com/provoware/game_more_core/actions/runs/40070628605).
- Repository Health: **PASS**, [Run #40070628628](https://github.com/provoware/game_more_core/actions/runs/40070628628).
- Status Sync: **PASS**, [Run #40070628579](https://github.com/provoware/game_more_core/actions/runs/40070628579).
- Release Acceptance: **PASS**, [Run #40070628569](https://github.com/provoware/game_more_core/actions/runs/40070628569).
- Release Package: **PASS**, [Run #40070628597](https://github.com/provoware/game_more_core/actions/runs/40070628597).

Diese Nachweise beziehen sich **nur auf den genannten Implementierungs-HEAD**. Der abschließende Dokumentations-Commit muss erneut geprüft werden. Der gesamte Vorrelease-Kandidat ist **nicht** freigegeben: Langzeitpartien, vollständige Recovery-Fehlermatrix, echter Browser-Menüzoom und Main-Integrity-Vorfälle bleiben offen.

## 24.10.2026 – Q01: Replay-Fehler darf kein Journal abschneiden

**Ausgangs-main:** `5faf41499c9302f807ef8f1d8b5d8dde1b760b6b`. **Entwicklungs-PR:** [#283](https://github.com/provoware/game_more_core/pull/283). **Implementierungs-HEAD:** `f2a6cfc897d5f4c9b7fbe32fb2136a1bf81e2cdc`.

**Fehlerursache:** Bei beschädigtem Journalende wurde das Originaljournal bereits vor dem fachlichen Replay auf den gültigen Teil gekürzt. Schlug das Replay danach fehl, war das Originaljournal bereits verändert, obwohl keine Wiederherstellung abgeschlossen war.

**Änderung:** `PersistenceKernel.recover` berechnet den Zielzustand zunächst vollständig im Arbeitsspeicher. Erst nach erfolgreichem Replay werden ein ungültiger Journalanhang gesichert, das Journal gekürzt und State/Meta aktualisiert. Bestehendes Format und reguläre Spielaktionen unverändert.

| Soll / Pflicht | Ist / Evidenz | Status |
|---|---|---|
| Q01: Replay-Fehler nach gültigem Snapshot und bestätigtem Event | `test_recovery_replay_atomicity.py::test_failed_replay_preserves_original_journal_and_checkpoints`; Bytevergleich Journal/State/Meta | PASS auf `c5aa4eb55f2baf4ba9db5ec498c212c1367f27ca`; finales Dokumentations-HEAD erneut prüfen |
| Q01: Erfolgreicher Replay mit beschädigtem Tail | `test_successful_replay_quarantines_tail_and_restores_state`; Quarantäne, genau ein Event, erneutes normales Öffnen | PASS auf `c5aa4eb55f2baf4ba9db5ec498c212c1367f27ca`; finales Dokumentations-HEAD erneut prüfen |
| Q01: Snapshot- und Meta-Schreibfehler / voller Datenträger / Crash bei Recovery | Fehler-Injektion für `atomic_write_json` und Wiederanlauf noch nicht vollständig | OFFEN |
| Q01: End-to-End-Langzeitpartie, Legacy-Migration, echtes Stromausfallverhalten | gesonderte vollständige Regression und reale Systemgrenzen nötig | OFFEN |
| Q04–Q13: Browserzoom, native Tastatur, Main-Integrität, Gesamtfreigabe | getrennte Prüfungen; Issues #277/#280 weiterhin klärungsbedürftig | OFFEN / BLOCKED; persönliche Abnahme zuletzt |

**Geplanter Test:** vollständiger `Runtime Core` samt beiden neuen Regressionen sowie die sechs PR-Prüfketten auf dem endgültigen Dokumentations-HEAD. `PASS` nur nach GitHub-Ergebnis. Keine echten Spielstände bearbeitet; keine Main-Änderung, kein Merge, kein Release.

**Nächste Pflicht:** Dateisystemfehler während Recovery-State-/Meta-Schreiben simulieren und nach Neustart auf unveränderte bestätigte Ereignisse und erneute Wiederherstellbarkeit prüfen. Danach längere echte Spielverläufe. **Spätere Verbesserungsidee:** Read-only Recovery-Vorschau mit Anzeige des letzten verifizierten Journalstands und der möglichen Replay-Ereignisse, damit der Nutzer vor einem Eingriff weiß, was wiederhergestellt werden kann.

**Verifizierte sechs PR-Prüfketten auf `c5aa4eb55f2baf4ba9db5ec498c212c1367f27ca` (24.10.2026):**
- Runtime Core: **PASS** – https://github.com/provoware/game_more_core/actions/runs/40090502601
- Presentation Core: **PASS** – https://github.com/provoware/game_more_core/actions/runs/40090502602
- Repository Health: **PASS** – https://github.com/provoware/game_more_core/actions/runs/40090502625
- Status Sync: **PASS** – https://github.com/provoware/game_more_core/actions/runs/40090502658
- Release Acceptance: **PASS** – https://github.com/provoware/game_more_core/actions/runs/40090502603
- Release Package: **PASS** – https://github.com/provoware/game_more_core/actions/runs/40090502606

**Wichtige Einschränkung:** Zwischen-HEAD `f2a6cfc897d5f4c9b7fbe32fb2136a1bf81e2cdc` hatte einen einmaligen Chromium-Timeout in Release Acceptance #40090424612, während der spätere Lauf #40090502603 PASS erreichte. Diese Instabilität bleibt als mögliche Browser-Testflakiness zu beobachten und zählt **nicht** als Freigabe des Gesamtprojekts. Die vorliegende Matrix-Dokumentation erhält einen neuen HEAD und muss erneut durch die PR-Gates.

## 24.10.2026 – Q01: Recovery-Schreibfehler / ENOSPC (Entwicklungs-PR #283)

**Basis:** `main` `5faf41499c9302f807ef8f1d8b5d8dde1b760b6b`. **Code-Commit:** `fee6f0e112b702ff9b505da2345596cc6072efaa`. **Test-Commit:** `c5c7cd00712a80ea07f088de1cccf0bddffa07f2`. **PR:** https://github.com/provoware/game_more_core/pull/283 (Entwurf).

**Fehler:** Recovery kürzte bei beschädigtem Journalende das Originaljournal und setzte die interne Schreibsperre zurück, **bevor** State und Metadaten erfolgreich geschrieben waren. Bei simuliertem vollem Datenträger konnte so ein unvollständiger Wiederherstellungsversuch bereits das Original verändern und den laufenden Kernel als beschreibbar erscheinen lassen.

**Änderung:** Erst Replay im Arbeitsspeicher, dann Quarantäne, danach State- und Meta-Schreiben; das Journal wird erst anschließend atomar ersetzt. Die interne Schreibsperre wird erst nach allen drei erfolgreichen Schritten aufgehoben. Bestehendes Journal-/Save-Format und Gameplay bleiben unverändert.

| Pflicht / Soll | Umsetzung / Test | Status |
|---|---|---|
| Q01 – ENOSPC beim State-Schreiben | `test_enospc_state_or_meta_keeps_original_journal_and_recovery_guard`; Originaljournal bytegleich, Recovery-Sperre aktiv, erneuter Recovery-Versuch | PASS (GitHub Runtime Core auf `a41a58882c834fc3acd3a222abcec80f0763a525`) |
| Q01 – ENOSPC beim Meta-Schreiben | dieselbe Regression mit zweitem Fehlerziel; bestätigtes Event beim Wiederanlauf genau einmal | PASS (GitHub Runtime Core auf `a41a58882c834fc3acd3a222abcec80f0763a525`) |
| Q01 – ENOSPC beim Journal-Ersatz | `test_enospc_journal_replacement_keeps_original_and_allows_retry`; Originaljournal bytegleich, erneut reparierbar | PASS (GitHub Runtime Core auf `a41a58882c834fc3acd3a222abcec80f0763a525`) |
| Q01 – ENOSPC beim Post-Recovery-Snapshot | `test_enospc_snapshot_after_recovery_leaves_playable_save`; normale Öffnung trotz Snapshot-Fehler möglich | PASS (GitHub Runtime Core auf `a41a58882c834fc3acd3a222abcec80f0763a525`) |
| Q01 – tatsächlicher Stromausfall, Verzeichnis-Fsync, Crash nach Snapshot-/Beleg-Schreiben | noch keine reale Systemprüfung; Mehrdatei-Transaktion ist kein vollständig atomarer Dateisystem-Commit | OFFEN |
| Q03 – vollständige Langzeitpartien und ältere Original-Saves | End-to-End- und Migrationsnachweise fehlen | OFFEN |
| Q04/Q05 – 800×600, 175–200-%-Browserzoom, native Tastatur | separate reale Browserprüfungen fehlen | OFFEN |
| Q10 – Main-Integrität #277/#280, Konflikt PR #282 | keine Schutzumgehung, keine Integration | BLOCKED / OFFEN |
| Benutzer-Endabnahme und Release | erst nach allen technischen Gates und eingefrorenem Kandidaten | ZURÜCKGESTELLT |

**Prüfplan:** `PYTHONPATH=src python3 -m unittest tests.runtime.test_recovery_write_failures -v`, vollständiger Runtime-Core und alle sechs PR-Gates auf endgültigem HEAD. Bis zum nachgewiesenen Ergebnis keine PASS-Einstufung. Kein Merge, kein Release. Nächste konkrete Implementierung: simulierte Unterbrechungen nach Snapshot-Index und Recovery-Beleg sowie mehrstufiger Wiederanlauf mit wiederholten bestätigten Events.

**Echte GitHub-Prüfungen auf `a41a58882c834fc3acd3a222abcec80f0763a525` (24.10.2026):** Runtime Core **311/311 PASS** [#40112008486](https://github.com/provoware/game_more_core/actions/runs/40112008486), Presentation Core **PASS** [#40112008604](https://github.com/provoware/game_more_core/actions/runs/40112008604), Repository Health **PASS** [#40112008515](https://github.com/provoware/game_more_core/actions/runs/40112008515), Status Sync **PASS** [#40112008699](https://github.com/provoware/game_more_core/actions/runs/40112008699), Release Acceptance **PASS** [#40112008587](https://github.com/provoware/game_more_core/actions/runs/40112008587), Release Package **PASS** [#40112008540](https://github.com/provoware/game_more_core/actions/runs/40112008540). Alle sechs Runs gehören zum genannten SHA. **Der anschließende Dokumentations-HEAD braucht neue CI; keine Gesamt-Vorrelease-Freigabe.**
