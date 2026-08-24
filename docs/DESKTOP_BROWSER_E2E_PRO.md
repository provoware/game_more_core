# BUNKERFREQUENZ – MULTI BROWSER E2E PRO

## Zweck

`DESKTOP-BROWSER-E2E-PRO` bleibt das zweite verpflichtende Release-Subgate neben `FAILURE-CONTAINMENT-PRO`, prüft den paketierten Benutzerpfad jetzt aber als echte Multi-Browser-Abnahme. Chrome/Chromium und Mozilla Firefox müssen denselben deterministischen Release-Kandidaten erfolgreich rendern.

## Abnahmeweg

Die Prüfung baut aus dem aktuellen, unveränderten Git-Stand genau einen deterministischen Release-Kandidaten und vergleicht dessen SHA-256 mit der bereits erfolgreichen Failure-Containment-Evidence. Dieser eine Candidate wird danach zweimal in frischen temporären Umgebungen geprüft:

1. `desktop_launcher_contract` – `START_BUNKERFREQUENZ.sh`, `BUNKERFREQUENZ.desktop` und `tools/start_orchestrator.py` müssen exakt den kanonischen Klickstartpfad bilden.
2. `clickstart_orchestrator` – das entpackte `START_BUNKERFREQUENZ.sh` wird real ausgeführt. Server, API, Nachvalidierung, `100 % / BEREIT` und tatsächliche Serverbeendigung nach dem CI-Exit müssen bestätigt sein.
3. `chromium_dom_ready` – der vorhandene echte Chrome-/Chromium-Acceptance-Pfad lädt denselben Candidate und verlangt den DOM-Zustand `● BEREIT` sowie eine reaktionsfähige Control-Deck-Oberfläche.
4. `firefox_dom_ready` – nativer Mozilla Firefox wird über den vorhandenen Geckodriver headless gestartet. Firefox lädt dieselben entpackten Candidate-Bytes; über das standardisierte WebDriver-Protokoll wird der echte DOM bis `● BEREIT` abgefragt und `/api/health` aus der Firefox-Seite selbst als `ready` bestätigt.

## Gleiche Release-Bytes

Es gibt keinen separaten Firefox-Build. Chromium und Firefox laufen innerhalb desselben `_single_run` gegen denselben zuvor gebauten ZIP-Candidate. Der einzige `candidate_sha256` wird sowohl mit FAILURE-CONTAINMENT als auch mit dem kombinierten Browser-Evidence-Receipt verbunden. Ein Browser kann deshalb keinen PASS für andere Release-Bytes liefern.

## Anti-Flake

Die vollständige Vier-Szenarien-Matrix läuft zweimal. Beide Statusvektoren müssen identisch und vollständig `PASS` sein. Unterschiedliche Ergebnisse werden `FLAKY`; reproduzierbare Fehler werden `FAIL`. Ein späterer Retry darf einen widersprüchlichen Browserlauf nicht zu PASS umdeuten.

## Evidence-Kette

Der Runner liest zuerst das bereits erzeugte `SUBGATE_EVIDENCE.json` von FAILURE-CONTAINMENT und akzeptiert es nur, wenn Source Commit, Source Tree, Candidate SHA-256 und `failure_containment_pro=PASS` exakt passen. Anschließend entstehen:

- `DESKTOP_BROWSER_E2E_EVIDENCE.json`
- `DESKTOP_BROWSER_E2E_EVIDENCE.json.sha256`
- ein kombiniertes `SUBGATE_EVIDENCE.json` mit beiden PRO-Gates

Erst dieses kombinierte Receipt wird an den Release Autopilot übergeben.

## Für Laien

Vor der finalen ZIP-Freigabe wird jetzt nicht nur geprüft, ob das Spiel theoretisch in zwei Browsern laufen sollte. Derselbe fertige Paketstand wird real einmal mit Chrome/Chromium und einmal mit Firefox geöffnet. Beide Browser müssen die Oberfläche vollständig bis „BEREIT“ laden. Scheitert nur einer davon, bleibt die Release-Freigabe gesperrt.

## Sicherheitsgrenzen

Keine Gameplaymutation, kein Save-Schema-Umbau, kein `sudo`, keine Paketinstallation und keine zweite Browser- oder Serverarchitektur. Firefox und Geckodriver werden nur verwendet, wenn sie bereits in der Testumgebung vorhanden sind; fehlen sie, schlägt das verpflichtende Gate geschlossen fehl.

## Spätere Erweiterungsidee

Als nächster Qualitätsschritt kann `RELEASE-EVIDENCE-CHAIN-PRO` Failure-, Multi-Browser-, Release-Evidence und finales Benutzer-ZIP in einer expliziten, maschinenprüfbaren SHA-256-Kette verbinden. Nutzen: Jeder Nachweis zeigt dann nicht nur auf dieselben Candidate-Bytes, sondern auch nachvollziehbar auf den jeweils vorherigen Evidence-Hash und das final tatsächlich ausgegebene ZIP.
