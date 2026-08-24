# BUNKERFREQUENZ – DESKTOP BROWSER E2E PRO

## Zweck

`DESKTOP-BROWSER-E2E-PRO` ist das zweite verpflichtende Release-Subgate neben `FAILURE-CONTAINMENT-PRO`. Es prüft nicht nur Dateien oder Unit-Tests, sondern den tatsächlich paketierten Benutzerpfad vom Linux-Klickstart bis zur reaktionsfähigen Browseroberfläche.

## Abnahmeweg

Die Prüfung baut aus dem aktuellen, unveränderten Git-Stand denselben deterministischen Release-Kandidaten und vergleicht dessen SHA-256 mit der bereits erfolgreichen Failure-Containment-Evidence. Danach läuft die Matrix zweimal in frischen temporären Umgebungen:

1. `desktop_launcher_contract` – `START_BUNKERFREQUENZ.sh`, `BUNKERFREQUENZ.desktop` und `tools/start_orchestrator.py` müssen im entpackten Paket vorhanden sein; Desktop und Startskript müssen ausführbar sein und dürfen nur auf den kanonischen Orchestratorpfad zeigen.
2. `clickstart_orchestrator` – das entpackte `START_BUNKERFREQUENZ.sh` wird real ausgeführt. Der Orchestrator muss Server, API, Nachvalidierung und kontrollierten CI-Exit bis `100 % / BEREIT` abschließen.
3. `chromium_dom_ready` – der vorhandene reale Browser-Acceptance-Pfad startet den paketierten Server, lädt die Oberfläche in Chrome/Chromium und verlangt den bestätigten DOM-Zustand `● BEREIT` sowie eine reaktionsfähige Control-Deck-Oberfläche.

## Anti-Flake

Beide Läufe müssen denselben vollständigen PASS-Statusvektor liefern. Unterschiedliche Ergebnisse werden `FLAKY`; reproduzierbare Fehler werden `FAIL`. Ein späterer Retry darf einen widersprüchlichen Lauf nicht still zu PASS erklären.

## Evidence-Kette

Der Runner liest zuerst das bereits erzeugte `SUBGATE_EVIDENCE.json` von FAILURE-CONTAINMENT und akzeptiert es nur, wenn Source Commit, Source Tree, Candidate SHA-256 und `failure_containment_pro=PASS` exakt passen. Anschließend entstehen:

- `DESKTOP_BROWSER_E2E_EVIDENCE.json`
- `DESKTOP_BROWSER_E2E_EVIDENCE.json.sha256`
- ein kombiniertes `SUBGATE_EVIDENCE.json` mit beiden PRO-Gates

Erst dieses kombinierte Receipt wird an den Release Autopilot übergeben. Damit kann `RELEASE_READY` nur entstehen, wenn beide PRO-Gates für dieselben Release-Bytes grün sind.

## Für Laien

Vor der finalen ZIP-Freigabe wird also automatisch genau das geprüft, was später beim normalen Start passieren soll: ZIP entpacken, Startdatei benutzen, lokalen Server hochfahren, Spielzustand laden und die echte Browseroberfläche bis „BEREIT“ rendern. Ein nur theoretisch korrekter Code reicht nicht.

## Sicherheitsgrenzen

Keine Gameplaymutation, kein Save-Schema-Umbau, kein `sudo`, keine Paketinstallation und keine zweite Browser- oder Serverarchitektur. Der PRO-Runner benutzt ausschließlich die bereits vorhandenen Start-/Browserwege.

## Spätere Erweiterungsidee

Als nächster Qualitätsausbau kann eine echte Multi-Browser-Matrix ergänzt werden, die neben dem verpflichtenden Chromium-DOM-Nachweis zusätzlich Firefox nativ auf demselben Kandidaten prüft und die Ergebnisse getrennt evidenziert. Nutzen: stärkere Release-Kompatibilität ohne den heutigen kanonischen Startpfad umzubauen.
