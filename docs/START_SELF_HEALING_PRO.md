# BUNKERFREQUENZ – START SELF-HEALING PRO

## Ziel

Der öffentliche Klickstart soll typische lokale Start- und Laufzeitfehler automatisch beheben, ohne Spielstände zu löschen, Systemrechte zu verändern oder eine Endlosschleife aus Neustarts zu erzeugen.

**Leitregel:** Jeder erkannte Fehler erhält eine definierte Recovery-Policy. Sicher reparierbare Fehler werden automatisch und begrenzt behoben. Fehler, die nur durch Datenverlust, `sudo`, Paketinstallation, unbekannte Fremdprozesse oder unkontrollierte Wiederholungen „behebbar“ wären, brechen stattdessen fail-closed mit `START_DIAGNOSE.txt` ab.

## Konkreter Freeze-Befund

Ein dauerhaft verwendeter Browser konnte unter derselben `127.0.0.1`-Adresse ältere statische UI-Dateien weiterverwenden. Besonders kritisch war eine ältere Fassung des Fokus-Moduls, deren `MutationObserver` durch eigene Klassenänderungen erneut ausgelöst werden konnte. Frische CI-Browserprofile sahen bereits die korrigierten Bytes, ein vorhandener Desktop-Browser konnte dagegen noch den alten Stand ausführen.

Die neue Startstufe schließt diese Lücke auf mehreren Ebenen:

- alle initialen Browserassets tragen eine gemeinsame explizite Asset-Revision;
- auch dynamisch nachgeladene UI-Module übernehmen exakt diese Revision;
- sichtbare Browserstarts erhalten zusätzlich eine neue `startup`-Adresse;
- der lokale Server liefert statische Dateien mit `no-store, no-cache, must-revalidate`;
- beide vorhandenen `MutationObserver` laufen während eigener DOM-Anpassungen abgekoppelt und bündeln externe Änderungen auf einen Render-Takt;
- die echte Browser-Abnahme akzeptiert `● BEREIT` nicht mehr allein: `Timeline wird geladen …` muss ebenfalls verschwunden sein.

## Self-Healing-Matrix

| Fehlerklasse | Automatische Reaktion | Grenze |
| --- | --- | --- |
| Wunschport belegt | auf automatisch freien Port wechseln | einmalige Portstrategie pro Start |
| erster Serverstart hängt/bricht ab | kontrollierter Neustart auf freiem Port | maximal 2 Startversuche |
| API während Warm-up noch nicht bereit | kurze gestaffelte Nachprüfung | 3 Prüfungen, danach Diagnose |
| alte Browser-/JS-Dateien im Cache | Asset-Revision + cache-busted Startadresse + `no-store` | keine Browserdaten werden gelöscht |
| Fokus-/Map-Observer reagiert auf eigene DOM-Änderung | Observer während eigener Änderung trennen, Mutation-Bursts zusammenfassen | Fokus-Hilfe deaktiviert sich nach 3 internen Fehlern statt die Seite zu blockieren |
| `/api/state`-Polling langsam/unterbrochen | nur ein Request gleichzeitig, Timeout im gemeinsamen Transport, exponentieller Backoff | maximal 30 s Backoff, kein Request-Sturm |
| GET-Transportfehler | begrenzte Wiederholung | 2 Retries |
| `/api/command`-POST mit bestätigter `command_id` | genau eine Transport-Wiederholung mit derselben ID | nur dieser bestätigte Replay-Pfad; Domain-/422-Fehler werden nie wiederholt |
| `/api/new-game` oder Checkpoint | keine automatische Schreibwiederholung | schützt vor falschem Bootstrap-Replay bzw. doppeltem Snapshot |
| Server/API fällt direkt nach Browserübergabe aus | kontrollierter Server-Neustart + erneute API-Prüfung | begrenzte Start-Recovery |
| Server/API fällt im laufenden Spiel aus | Health-Wächter startet denselben kanonischen Server neu; bei neuer Adresse Browserübergabe erneut | maximal 3 Recoveries in 5 Minuten |
| wiederkehrender Fehler über Recovery-Grenze | fail-closed + Diagnose | keine Neustartspirale |
| Save benötigt vorhandene sichere Recovery | vorhandener `GameRecoveryService` | keine zweite Recovery-Engine |
| Save irreparabel / Pfad nicht beschreibbar / Pflichtdatei fehlt / Python zu alt | klare Diagnose und Abbruch | keine Datenlöschung, kein `sudo`, keine Paketinstallation |

## Transport-Sicherheit

`web/a4/client_resilience.js` ist eine dünne Transporthärtung vor der bestehenden UI. Es enthält keine Domainlogik.

- GET/HEAD dürfen bei Transport-/Serverfehlern begrenzt wiederholt werden.
- Ein schreibender POST wird nur auf dem ausdrücklich replay-sicheren Pfad `/api/command` automatisch einmal wiederholt und auch dort nur mit nichtleerer `command_id`.
- `/api/new-game` wird trotz `command_id` nicht automatisch wiederholt, weil ein bereits erfolgreicher Bootstrap bei verlorener Antwort derzeit nicht als identischer Replay bestätigt werden kann.
- Ein manueller Checkpoint wird ebenfalls nicht automatisch erneut geschrieben.
- Alle API-Aufrufe erhalten ein hartes Zeitlimit über Header und vollständigen Response-Body, damit ein hängender Request die Oberfläche nicht dauerhaft im Zustand „busy“ festhält.

## Laufzeit-Wächter

Nach erfolgreichem Klickstart bleibt der Orchestrator zuständig für genau den von ihm gestarteten Serverprozess. Alle 10 Sekunden wird dessen Prozess- und API-Zustand geprüft. Eine einzelne API-Abweichung löst noch keinen Neustart aus; erst eine bestätigte zweite Abweichung führt zur Recovery.

Innerhalb von fünf Minuten sind höchstens drei automatische Recoveries erlaubt. Wird diese Grenze erreicht, gilt das Verhalten als wiederkehrender Fehler und nicht mehr als transienter Ausfall. Der Startpfad stoppt dann kontrolliert und schreibt die Diagnose, statt das Problem durch weitere Neustarts zu verdecken.

## Für Laien

Im Normalfall bleibt der Start unverändert: `START_BUNKERFREQUENZ.sh` bzw. die Desktop-Datei öffnen das Spiel. Neu ist, dass typische lokale Störungen selbstständig abgefangen werden. Wenn eine sichere Reparatur möglich ist, steht sie im Startstatus unter `AUTO-AUFLÖSUNG`. Wenn eine automatische Reparatur riskant wäre, wird nichts gelöscht oder am System verändert; stattdessen erklärt `START_DIAGNOSE.txt`, was konkret nicht sicher lösbar war.

Bei einem Browserdialog wie „Seite reagiert nicht“ sollte der nächste Start automatisch eine neue cache-sichere URL verwenden. Ein alter festgefahrener Tab kann geschlossen werden; der neue Start öffnet die aktuelle UI-Fassung.

## Sicherheitsgrenzen

- kein `sudo`
- keine automatische Paketinstallation
- kein Löschen oder Zurücksetzen eines Spielstands als „Reparatur“
- keine Beendigung fremder Prozesse
- keine zweite Server-, Persistence- oder Recovery-Architektur
- keine unendlichen Retries
- keine Wiederholung nicht-idempotenter oder nicht ausdrücklich replay-sicherer Schreiboperationen

## Spätere Erweiterungsidee

Ein eigener `CLIENT-FREEZE-TELEMETRY-LOCAL`-Slice könnte ausschließlich lokal und opt-in die Dauer von Main-Thread-Lag, API-Timeouts und Recovery-Ereignissen in einer kleinen rotierenden Diagnosedatei erfassen. Nutzen: sporadische Desktop-Freezes wären nachträglich messbar, ohne Telemetriedaten nach außen zu senden oder Gameplayzustand anzutasten.
