# AUTOSTART-CHAOS-MATRIX

Diese Abnahme belastet den vorhandenen `AUTOSTART-ORCHESTRATOR` gezielt mit typischen Startstörungen. Sie verändert **keine Produktionslogik** und führt keine versteckten Fehler-Schalter in den normalen Start ein.

## Ziel

Nachweisen, dass bekannte Fehler- und Recovery-Pfade deterministisch, verständlich und fail-closed reagieren.

## Matrix

| Szenario | Erwartung |
|---|---|
| Wunschport belegt | automatische Umstellung auf freie Portwahl, Start läuft weiter |
| Spielstandziel nicht beschreibbar | kontrollierter Abbruch, Fehlerklasse `filesystem_permissions`, `JETZT BEHEBEN` vorhanden |
| kein unterstützter Browserstarter | gelber Komfortzustand, kein falscher roter Spielabbruch |
| erster Serverstart zu langsam | genau ein Recovery-Neustart mit freier Portwahl |
| API antwortet zunächst verzögert | genau eine Kurz-Nachprüfung; bei Erfolg normale Nachvalidierung |
| erster Serverstart bricht vor Bereitschaft ab | genau ein zweiter Startversuch; danach normaler Start oder fail-closed |

## Testtechnik

Die Matrix verwendet ausschließlich Test-Fakes und kontrollierte lokale Bedingungen. Der echte Orchestrator-Code wird aufgerufen; ersetzt werden nur externe Randbedingungen wie Serverprozess, Browserverfügbarkeit oder künstlich verzögerte API-Antworten.

Es gibt bewusst **keine** produktiven Optionen wie `--simulate-crash` oder `--break-api`. Dadurch kann ein normaler Spielerstart nicht versehentlich in einen Testfehlerzustand versetzt werden.

## Sicherheitsgrenzen

- kein `sudo`
- keine Paketinstallation
- keine Gameplay-/Save-/Journaländerung
- keine zweite Recovery-Engine
- keine Systemzeit als Entscheidungsautorität
- keine Änderung der normalen Retry-Anzahl

## Regression

`tests/release/test_autostart_chaos_matrix.py` prüft alle sechs Matrixfälle. Ein erfolgreicher Test bedeutet nicht nur, dass eine Exception geworfen wurde, sondern dass der erwartete Ampel-, Diagnose- oder Recovery-Vertrag sichtbar erreicht wurde.
