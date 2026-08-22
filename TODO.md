# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Versionierte Runtime-Baseline:** `0.5.2-alpha.1`
- **Zuletzt remote validierte Feature-Iteration:** `0.8.1 – Event State Foundation`
- **0.8.1-Referenz:** PR #48, Head `79cc26bec0a780322874ea6f3ced458e8ee72bd6`
- **0.8.1-Remote-Abnahme:** Runtime Core `32537531324`, Presentation Core `32537531305`, Repository Health `32537531303` grün
- **Aktive Iteration:** `0.8.2 – Equipment & Economy`
- **0.8.1-Abschluss:** PR #48 gemergt als `9ed0dbd8928014777fa4b100a7c65ba4c30ca04e`
- **Fortschritt zum ersten spielbaren Alpha-Release:** `70 %` (Planungswert; Release-Gate noch nicht erfüllt)
- **Aktueller Release-Blocker:** kein mit der Runtime verbundener Client und noch kein vollständiger Event-/Economy-Loop

## Release-Ziel und Abnahme

**Ziel:** Ein lokal startbares Alpha verbindet Character Forge, Equipment/Economy und den vollständigen Event-Loop über bestätigte Journal-Ereignisse mit einer bedienbaren Oberfläche.

**Abnahme:** Aus einem frischen Checkout lässt sich der dokumentierte Startweg ausführen; eine Person ohne Codewissen kann ein Event planen, Equipment beschaffen, das Event samt Krise abschließen, das Ergebnis speichern und nach Neustart identisch wiederherstellen.

**Bewusste Nicht-Ziele des ersten lokalen Alpha-Releases:** Telegram-/Netzwerk-Sync, öffentlicher Serverbetrieb und native GitHub-Branch-Protection. Diese Punkte dürfen den lokalen Spielkern nicht verzögern.

## Repository Guard

- [x] `REPOSITORY_GUARD_MANIFEST.json` als kanonische Merge-/Health-Policy angelegt
- [x] `tools/repository_health.py` ohne externe Abhängigkeiten implementiert
- [x] `Repository Health` als eigener PR-/main-/Merge-Group-Gate angelegt
- [x] Runtime Core und Presentation Core liefern bei jedem PR einen Required-Check-Status
- [x] Guard prüft JSON, Python-Struktur/Compile, Konfliktmarker, Status-/Versionskonsistenz, öffentliche Exporte und kanonische Symbole
- [x] Guard blockiert veraltete versionsgebundene Feature-Branches
- [x] Workflow blockiert PR-Heads, die den aktuellen `main` nicht enthalten
- [x] `/safe-merge` prüft Berechtigung, aktuellen `main`, exakten PR-Head, drei grüne Kern-Gates und offene Review-Threads unmittelbar vor Merge
- [x] normale `/safe-merge`-PRs dürfen den Guard-/CI-Sicherheitsrand nicht selbst verändern
- [x] Main Integrity prüft Merge-Provenienz nach Änderungen auf `main`
- [x] Eventual-Consistency-Hotfix: Merge exakt einmal; ausschließlich die nachgelagerte Provenienz-Leseprüfung nutzt begrenzten Retry
- [x] PR #38 End-to-End: Runtime Core `32528078989`, Presentation Core `32528078992`, Repository Health `32528078926`, `SAFE MERGE PASS`
- [x] Safety Receipt PR #39: Runtime Core `32528915005`, Presentation Core `32528914997`, Repository Health `32528915004`, `SAFE MERGE PASS`
- [x] Main-Integrity-Incident #40 für Direkt-Commit `fb96a489...` analysiert: Guard reagierte korrekt auf fehlende PR-Provenienz; Inhalt später in PR #41 erneut grün validiert; Incident geschlossen
- [x] versehentlichen leeren `tmp`-Direktcommit über gezielten PR #47 entfernt; Runtime Core `32536504014`, Presentation Core `32536504089`, Repository Health `32536504068`, `SAFE MERGE PASS`

## 0.6.0 – Repository-/Presentation-Reparatur

- [x] beschädigte doppelte `character_projection.py` auf eine kanonische Implementierung zurückgeführt
- [x] widersprüchliche Projection-Tests konsolidiert
- [x] eindeutige Presentation-Package-Exporte wiederhergestellt
- [x] `Presentation Core` als eigener zielgerichteter CI-Gate angelegt
- [x] Release-Baseline und aktive Entwicklungsiteration in den Info-Dateien getrennt
- [x] PR #22 mit Runtime Core + Presentation Core grün gemergt
- [x] konkurrierende Presentation-PRs #15–#21 mit Begründung geschlossen

## 0.6.1 – Application-Grenze für Presentation

- [x] `can_edit_profile`, `can_undo_profile`, `can_execute_action` ausschließlich aus der Application ableiten
- [x] Profilupdate, Profil-Undo und Action-Ausführung über **einen** Command-Dispatcher routen
- [x] notwendige IDs validieren und über die zuständigen bestehenden Services führen
- [x] UI-gesteuerte Balanceparameter nicht freigeben
- [x] Profilupdate, Undo und Action-Wiederholung idempotent testen
- [x] Projection erhält bestätigte Capabilities als begrenzte defensive Kopie
- [x] PR #24: Runtime Core `32510846508` + Presentation Core `32510846537` grün
- [x] PR #24 gemergt (`25006d07d33199fea2db8208c192ca2f6fa1095d`)

## 0.6.2 – Lokaler Presentation-State + bestätigtes Feedback

- [x] unveränderlichen Zustand für `overview`, `skills_traits`, `biography` angelegt
- [x] lokale View-/Filter-/Dismiss-Transitionen ohne Persistenzwirkung umgesetzt
- [x] Biografie-Filter nutzt `BIOGRAFIE_MANIFEST.json`
- [x] bestätigte Journalrecords über Application-Abfrage bereitgestellt
- [x] Level-, Skill-, Trait-, Spezialisierungs- und Resonanzfeedback projiziert
- [x] deterministische Feedback-IDs aus bestätigten Event-IDs
- [x] sichtbare Feedbacktexte ausgelagert
- [x] Reduced Motion fachlich zustandsneutral
- [x] End-to-End `Command → Commit → Eventquery → Feedback → Projection`
- [x] idempotenter Replay erzeugt kein doppeltes Feedback
- [x] PR #26: Runtime Core `32511953788` + Presentation Core `32511953619` grün
- [x] PR #26 gemergt (`5161cb42c2b0d38fcb69ea6bd20f9dc5ce1b283a`)

## 0.6.3 – Gemeinsame Komponenten + A4 Ops Deck

- [x] acht gemeinsame Komponenten implementiert
- [x] Komponenten erhalten nur Projection-Blöcke und lokalen Presentation-State
- [x] `ProfileEditor` nutzt ausschließlich den zentralen Command-Dispatcher-Vertrag
- [x] `ProgressFeedback` nutzt bestätigte Feedback-Projektion und lokale Dismiss-/Reduced-Motion-Regeln
- [x] A4 Ops Deck als Workflow `Ziel → Aktion → Ergebnis → Entwicklung → nächstes Ziel`
- [x] maximal drei Primäraktionen; vierte Aktion wird abgewiesen
- [x] 44-px-Ziele, 3-px-Fokus, High-Contrast und Farbe+Icon+Text aus Manifestvertrag
- [x] leere optionale Bereiche erfinden keine Daten
- [x] Profiländerungen laufen über den bestätigten Application-Weg
- [x] PR #28: Runtime Core `32514970109` + Presentation Core `32514970398` grün
- [x] PR #28 gemergt (`49603304960147c326953474174aafcff366dcd7`)

## 0.6.4 – A3 Cinematic Forge

- [x] A3 verwendet dieselbe Projection und exakt dieselben acht Komponenten wie A4
- [x] A3 übernimmt Primäraktionen direkt aus dem validierten A4-Interaktionsvertrag
- [x] Character Stage, Live-Status, Skill-/Trait-Netz und Drawer definiert
- [x] sechs Progressionsfeedbackarten an katalogisierte Animationen gebunden
- [x] Reduced Motion und fail-soft statische Fallbacks
- [x] Vertragstest A3↔A4 für Komponenten, Commands, Accessibility und Primäraktionslimit
- [x] Runtime Core `32516833552` + Presentation Core `32516833514` auf PR #29 grün
- [x] PR #29 gemergt (`53f0617ce0c00051c5fae481c43e4ff048dddf94`)

## 0.6.5 – Ranking / Network Foundation

- [x] Ranking-Projektion für beliebig viele Spieler
- [x] Top 10 als Standard und `ALLE ANZEIGEN`
- [x] Sortierung nach Level, Skills, Ruf, Events, Clubs und Resonanz
- [x] Competition Ranking mit stabiler Gleichstandsregel
- [x] Events/Clubs nur aus `server_confirmed_transaction`-Datensätzen
- [x] fehlende Network-Metriken bleiben `null` und unranked
- [x] fehlende Sync-Daten werden `unknown` / `NICHT BESTÄTIGT`, ohne Presence abzuleiten
- [x] falsche Autorität, unbekannte Metriken, doppelte IDs und Character-Mismatch fail-closed
- [x] sichtbare Ranking-/Sync-Texte ausgelagert
- [x] Runtime Core `32517683276` + Presentation Core `32517683263` auf PR #30 grün
- [x] PR #30 gemergt (`4090c3e2118e81d0927fbc7a5cfcdf48190631e9`)

## 0.7 – Spielbarer Character-Forge-Vertical-Slice

`Profil → Training/Aktion → Skill-/Trait-Fortschritt → Feedback → Biografie → Autosave → Undo → Reload`

### 0.7.1 – A4 Action-Auswahl

- [x] alle 20 Manifest-Actions als kanonische A4-Auswahlliste projiziert
- [x] Dauer, Voraussetzungen und gewichtete erwartete Skillwirkung angezeigt
- [x] nicht bestätigte Voraussetzungen sperren die Action fail-closed
- [x] fehlende Energie-/Stresswerte ausdrücklich als nicht festgelegt markiert
- [x] PR #31: Runtime Core `32519042006` + Presentation Core `32519041908` grün
- [x] PR #31 gemergt (`888be18146197272578f4baa5516f78a894d9464`)
- [x] Review-P1: Auswahl enthält kein scheinbar ausführbares Teil-Command mehr
- [x] `build_action_execute_command(...)` erzeugt erst mit `command_id` und `action_instance_id` einen dispatcher-fertigen Command
- [x] A4 prüft `can_execute_action` beim Zusammensetzen erneut und sperrt stale Auswahlzustände

### 0.7.2 – Ressourcenwirkung + vollständiger Ablauf

- [x] Energie-/Stresswirkung fachlich für alle 20 Actions katalogisiert
- [x] Energie-/Stresswirkung im Resolver deterministisch angewendet und auf `0–100` begrenzt
- [x] `character.resources_changed` als katalogisiertes, replaybares Journal-Ereignis eingeführt
- [x] Training/Aktion → Progression → bestätigtes Feedback verbunden
- [x] Biografie-Eintrag aus bestätigten relevanten Actions deterministisch und atomar integriert
- [x] 60-Sekunden-Autosave und Snapshot im Character-Forge-Session-Ablauf verwendet
- [x] Undo nur über bestehende kompensierende Regeln angeboten; kein inkonsistentes pauschales Action-Undo
- [x] Reload/Recovery inklusive Ressourcen-Replay im vollständigen Vertical-Slice getestet
- [x] A4 und A3 auf denselben bestätigten Status-, Biografie- und Feedbackzustand zurückprojiziert
- [x] Legacy-Testfixtures an den neuen Pflicht-Ressourcenvertrag angepasst, ohne Produktlogik aufzuweichen
- [x] PR #41, Head `5f7ded400a5fca1ee25307797628ab2584de9812`: Runtime Core `32533954380`, Presentation Core `32533954387`, Repository Health `32533954406` grün
- [x] PR #41 nach erfolgreicher Abnahme nach `main` übernommen (`a7544abd923787d20e174c9eced54f548753c801`)
- [x] README visuell neu strukturiert und Einsteigerpfad verbessert
- [x] eigene verständliche [`Spieleranleitung`](docs/SPIELERANLEITUNG.md) ergänzt

## P0 – Pflichtpfad zum ersten spielbaren Alpha-Release

Die folgenden Pakete der 0.8-Event-/Wirtschaftsintegration werden ohne parallele Featurearbeit in dieser Reihenfolge abgeschlossen. Ein späteres Paket beginnt erst, wenn der exakte Head des vorherigen Pakets lokal geprüft, remote durch `runtime-core`, `presentation-core` und `repository-health` bestätigt und regelkonform übernommen wurde.

### 0.8.1 – Event State Foundation

- [x] `EventState` als eigener Domain-State neben `CharacterState` implementiert
- [x] Ort mit `location_id`, Anzeigename, Region und explizitem Zugangsstatus definiert
- [x] Event-Budgetrahmen in Cent ohne vorgezogene Economy-Ledger-Logik definiert
- [x] Acts, Crew und Equipment-Readiness als streng validierte eindeutige Listen definiert
- [x] offset-aware Zeitfenster mit `end > start` validiert
- [x] Sicherheitsstatus `unreviewed / cleared / restricted / blocked` definiert
- [x] Phasenmaschine `draft → planning → procurement → transport → setup → soundcheck → live/crisis → teardown → settlement → completed` implementiert
- [x] physische Phasen an Ort, Zugangsstatus, Zeitfenster und `safety_status=cleared` gebunden
- [x] `event.created`, `event.planning_updated`, `event.phase_changed` journalfähig gemacht
- [x] monotone Eventrevision und Stale-Write-Schutz implementiert
- [x] identische Event-Commands idempotent; gleiche Command-ID mit anderem Inhalt fail-closed
- [x] Character-/Profil-Commits so gehärtet, dass sie den `event`-State-Block nicht überschreiben
- [x] Event-Commits erhalten bestehende `character`-Daten
- [x] kombiniertes Character+Event-Recovery-Replay implementiert
- [x] Fault-Injection-Test für durable Eventänderung vor State-Write angelegt und remote bestanden
- [x] Manifest-/Domain-Phasenabgleich als Regressionstest angelegt und remote bestanden
- [x] Vertrag, Schema, Runtime-Manifest, README und Repository-Navigation ergänzt
- [x] Runtime Core `32537531324` auf Head `79cc26bec0a780322874ea6f3ced458e8ee72bd6` grün
- [x] Presentation Core `32537531305` auf demselben Head grün
- [x] Repository Health `32537531303` auf demselben Head grün
- [x] PR #48 auf Head `79cc26bec0a780322874ea6f3ced458e8ee72bd6` mit allen drei Kern-Gates grün
- [x] PR #48 als `9ed0dbd8928014777fa4b100a7c65ba4c30ca04e` nach `main` übernommen

### 0.8.2 – Equipment & Economy

**Abnahmeeinheit:** Katalog, Besitz, Reservierung, Transaktion und Recovery bilden einen gemeinsamen Vertical Slice (durchgängiger Funktionsschnitt). Kein Bestandteil wird allein als fertige Economy-Stufe freigegeben.

- [ ] Equipment-Katalog und Inventarbesitz als getrennte Zustände definieren
- [ ] dynamische Marktpreise datengetrieben und deterministisch modellieren
- [ ] Kaufen, Verkaufen und Verbrauchen über katalogisierte Inventory-/Economy-Events führen
- [ ] Budgetänderungen nur aus bestätigten Economy-Transaktionen ableiten
- [ ] Kompensationsregeln für reversible Economy-Transaktionen konkretisieren
- [ ] Event-Equipment-Anforderungen gegen bestätigten Besitz/Reservierung auflösen
- [ ] Save/Recovery/Idempotenz für Economy und Inventar testen
- [ ] gesamten Economy-Vertical-Slice auf demselben Head lokal und mit allen drei Remote-Gates abnehmen

### 0.8.3 – Vollständiger Event-Loop

- [ ] `Planung → Einkauf → Transport → Aufbau → Soundcheck → Event → Krise → Abbau → Abrechnung` als zusammenhängenden Ablauf implementieren
- [ ] Phasenaktionen und Voraussetzungen an EventState anbinden
- [ ] Krisen und Incident-Auflösung journalfähig machen
- [ ] Abrechnung, Ruf- und Character-Folgen aus bestätigten Ergebnissen ableiten
- [ ] A4/A3 um Event-/Economy-Projektionen erweitern, ohne Domain-State direkt zu schreiben
- [ ] vollständigen Event-Loop inklusive Save/Recovery testen
- [ ] Spieleranleitung um Eventplanung und Wirtschaft erweitern

### Release-Kandidat – spielbarer lokaler Client

- [ ] vor Client-Arbeit den vollständigen 0.8.3-Event-Loop auf demselben Head lokal und mit allen drei Remote-Gates bestätigen
- [ ] erst danach A4 als kleinsten schreibenden Client an den bestehenden Command-Dispatcher anbinden; keine zweite Domain- oder Persistenzlogik im Client
- [ ] laiengerechten Ersteinstieg `Crew wählen → Event planen → Equipment beschaffen → Event abschließen → Ergebnis prüfen` bereitstellen
- [ ] Start aus frischem Checkout mit einem dokumentierten Befehl und ohne manuelle Datenreparatur nachweisen
- [ ] deterministischen Smoke-Test `neues Spiel → Event-Loop → Save → Neustart → Recovery` mit festem Seed ergänzen
- [ ] verständliche Fehlermeldungen für ungültige Eingaben, gesperrte Phasen und fehlgeschlagene Wiederherstellung anzeigen
- [ ] Release-Checkliste auf exaktem Head abnehmen: Runtime Core, Presentation Core, Repository Health, 0 offene Review-Threads
- [ ] erst nach grüner Abnahme Version, Release Notes und reproduzierbares Release-Artefakt festlegen

## P1 – Härtung nach dem lokalen Alpha

- [ ] Native GitHub-Branch-Protection/Ruleset aktivieren, sobald ein geeigneter Admin-Schreibweg verfügbar ist: `runtime-core`, `presentation-core`, `repository-health` verpflichtend + Branch aktuell + Conversation Resolution
- [ ] 0.9 Network / Telegram Sync als eigenen Server-/Transportvertrag planen; gemeinsame Ressourcen bleiben bis zur Serverbestätigung unbekannt

## Später

- [ ] Optionalen Start-Selbsttest mit zeitlich begrenztem HTTP-Aufruf ergänzen; Nutzen: Support kann Dateivorprüfung, Serverbindung und erreichbare Startseite mit einem nicht blockierenden Befehl gemeinsam nachweisen.
- [ ] Kanonisches Blueprint-WebP aus der dokumentierten Originalquelle reproduzierbar neu exportieren und die überwiegend transparente aktuelle Datei erst nach visueller Abnahme ersetzen; Nutzen: vollständige Pixelreferenz statt formal ladbarer, aber visuell unbrauchbarer Fläche.
- [ ] HTML-Blueprint über einen schreibgeschützten Adapter mit fixture-basiertem Projection-JSON speisen und per Vertragstest nachweisen, dass fehlende oder unbestätigte Werte sichtbar leer bleiben; Nutzen: realistische UI-Auswertung ohne zweiten Domain-Schreibweg.
- [ ] Für den HTML-Blueprint einen automatisierten visuellen Kontrast- und Viewport-Nachweis bei 390, 900 und 1440 Pixeln ergänzen; Nutzen: die neue Blickführung bleibt bei späteren UI-Erweiterungen lesbar und regressionssicher.
- [ ] Recovery-Berichte um eine maschinenlesbare Fehlerkategorie ergänzen, damit eine spätere Oberfläche beschädigtes JSON, fehlende Felder und falsche Datentypen verständlich unterscheiden kann, ohne Fehlermeldungstext auszuwerten.
- [ ] Recovery-Receipt um die Anzahl übersprungener Snapshot-Kandidaten ergänzen, damit Support und spätere Oberfläche einen erfolgreichen Rückfall auf einen älteren Checkpoint sichtbar machen können, ohne ungültige Inhalte offenzulegen.
- [ ] Einen geführten Fünf-Minuten-First-Run mit anonymem lokalem Abschlussbeleg ergänzen; Nutzen: Der Release kann nicht nur technisch starten, sondern wird auch ohne Vorwissen überprüfbar verstanden.
- [ ] Einen maschinenlesbaren Economy-Replay-Abnahmebeleg mit festem Seed definieren; Nutzen: Katalog, Besitz, Reservierung, Transaktion und Recovery bleiben bei späteren Erweiterungen als zusammenhängender Slice nachweisbar.
- [ ] Repository Health um einen Abschlussabgleich zwischen gemergten Meilensteinen in `PROJEKTSTATUS.json`, `TODO.md` und `README.md` erweitern; Nutzen: bereits erledigte Freigabeschritte blockieren die Folgeiteration nicht erneut und Statuspflege verursacht weniger Nacharbeit.

## Abgeschlossene Meilensteine

- [x] **0.4.0** Architekturvertrag, Character-Forge-Foundation, 11 Figuren und gleiche Startwerte
- [x] **0.4.1** Trait Engine, Progression, Spezialisierungen und deterministischer Simulator
- [x] **0.4.2** Persistence Contract, Autosave, Undo, Snapshot-/Recovery-Regeln
- [x] **0.4.3** vier Industrial-Brutalist-UI/UX-Blueprints
- [x] **0.4.4** 20 datengetriebene Gameplay Actions
- [x] **0.5.0** Headless Character-/Action-/Persistence-Core
- [x] **0.5.1** Snapshot-Replay, Recovery, Fault Injection und Profil-Undo
- [x] **0.5.2** Trait-Auswirkungen, Soft-Konflikte und Open-End-Resonanz
- [x] **0.6 Foundation** Presentation-Vertrag und Character-/Biografieprojektion
- [x] **0.6.1** Application-Capabilities + zentraler Command-Dispatcher
- [x] **0.6.2** lokaler Presentation-State + bestätigtes Progressionsfeedback
- [x] **0.6.3** gemeinsame Komponenten + A4 Ops Deck
- [x] **0.6.4** A3 Cinematic Forge
- [x] **0.6.5** Ranking / Network Foundation
- [x] **0.7.1** A4 Action-Auswahl
- [x] **0.7.2** Ressourcenwirkung + kompletter Character-Forge-Vertical-Slice

## PR-Regel

Für dieselbe Zielstelle wird nur **ein aktiver Implementierungs-PR** geführt. Normale PRs nach `main` werden ausschließlich über `/safe-merge` übernommen. Dafür müssen `runtime-core`, `presentation-core` und `repository-health` auf exakt dem aktuellen PR-Head vorhanden und grün sein; der Branch muss aktuellen `main` enthalten und alle Review-Threads müssen gelöst sein. Änderungen an Guard-/CI-Sicherheitsdateien benötigen einen ausdrücklich auditierten Security-Bootstrap-PR. Native GitHub-Branch-Protection bleibt eine zusätzliche noch offene serverseitige Härtung.
