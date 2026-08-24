# BUNKERFREQUENZ – FAILURE CONTAINMENT PRO

## Zweck

`0.8.8-FAILURE-CONTAINMENT-PRO` ist das Robustheits-Subgate des Release Autopilot PRO. Es verändert keine Gameplay- oder Recovery-Regel. Es prüft, ob der bereits vorhandene Start-, Server- und Persistenzpfad unter kontrollierten Randbedingungen deterministisch fail-closed bleibt oder sauber recovered.

## Abgrenzung

Browser-Liveness, KDE-Doppelklick, Firefox/Chromium und DOM-Mutationsbudgets gehören ausschließlich zu `desktop_browser_e2e_pro`. FAILURE-CONTAINMENT testet deshalb Paketserver, lokale API, Start-/Recovery-Verträge und Persistenzbedingungen ohne Headless-Browser als Fremdvariable.

## Matrix

Die Matrix besteht aus sechs Szenariogruppen und wird zweimal in voneinander getrennten temporären Umgebungen ausgeführt:

1. `path_locale_matrix` – entpacktes Release unter Leerzeichen/Umlauten und langem Pfad sowie `C.UTF-8/UTC` und `C/Europe-Berlin`; `/api/health` und `/api/state` müssen bestätigt antworten.
2. `process_ownership` – ein fremder Sentinel-Prozess muss den Test überleben; der eigene Paketserver muss nach dem kontrollierten Ende vollständig verschwunden sein.
3. `resource_stress` – paketierter Server unter begrenzten File Descriptors und begrenztem virtuellen Adressraum; Health und State müssen weiterhin erreichbar sein.
4. `port_collision` – real belegter Loopback-Port muss kontrolliert mit EADDRINUSE-Erklärung scheitern; der separate Bind-Race-Vertrag beweist den einmaligen Orchestrator-Recovery-Neustart auf Port 0.
5. `fault_contract_regressions` – ENOSPC/Dateisystemfehler werden fail-closed und als `filesystem_permissions` diagnostiziert; Anti-Flake- und Bind-Race-Verträge werden direkt geprüft.
6. `crash_save_upgrade_recovery` – bestehende Journal-/Snapshot-/Resource-Recovery-Regressionen plus Legacy-State-Lesekompatibilität laufen unverändert durch.

## Anti-Flake-Vertrag

Die sechs Statusvektoren werden in zwei frischen Läufen erzeugt. Nur zwei vollständig grüne und identische Statusvektoren ergeben `PASS`.

- unterschiedliche Ergebnisse → `FLAKY`
- identische Fehler → `FAIL`
- zwei vollständig identische PASS-Läufe → `PASS`

Ein Retry darf einen vorherigen Widerspruch nicht in PASS umdeuten.

## Evidence

Der Runner erzeugt:

- `FAILURE_CONTAINMENT_EVIDENCE.json`
- `FAILURE_CONTAINMENT_EVIDENCE.json.sha256`
- `SUBGATE_EVIDENCE.json`

Die Evidence bindet den Nachweis an Source Commit, Source Tree und zusätzlich den SHA-256 des deterministisch gebauten Kandidaten. Vor der Source-Erfassung muss der komplette Git-Working-Tree sauber sein; dadurch kann kein Paket aus abweichenden lokalen Bytes einen PASS für den aufgezeichneten Commit erben.

OS-vergebene Laufzeitwerte wie Prozess-IDs oder dynamische Portnummern gehören nicht in den gehashten Evidence-Vertrag. Die Evidence enthält dafür stabile semantische Diagnosen, damit gleichartige Läufe derselben Quelle reproduzierbar vergleichbar bleiben.

Der Release Autopilot akzeptiert den Subgate-PASS nur im bestehenden source-gebundenen Evidence-Vertrag.

## Sicherheitsgrenzen

Keine Produktions-Fault-Schalter, kein `sudo`, keine Paketinstallation, keine Änderung des Save-Schemas, keine neue Recovery-Engine und keine Gameplaymutation. Fehler werden testseitig oder über reale lokale Ressourcenbedingungen erzeugt.

## Releasewirkung

Nach erfolgreichem FAILURE-CONTAINMENT steht `failure_containment_pro=PASS`. Solange `desktop_browser_e2e_pro` noch `NOT_RUN` ist, bleibt der Gesamtzustand korrekt `QUARANTINE` und es wird weiterhin kein Benutzer-ZIP promoted.
