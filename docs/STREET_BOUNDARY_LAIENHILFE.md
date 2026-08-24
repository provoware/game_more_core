# Street-Grenzwerte – Laienhilfe

## Was wurde geprüft?

Straßenbegegnungen dürfen Energie, Stress und Ruf verändern. Energie und Stress sind im Spiel auf **0 bis 100** begrenzt; neue Street-Ergebnisse dürfen Ruf nicht unter **0** drücken.

Der Grenzwert-Audit prüft deshalb ausdrücklich die kritischen Richtungen:

- positive Effekte dürfen Energie nicht über 100 und Stress nicht unter 0 drücken,
- negative Effekte dürfen Energie nicht unter 0 und Stress nicht über 100 drücken,
- negative Rufeffekte dürfen bei neuen Street-Ergebnissen den kanonischen Ruf-Floor 0 nicht unterschreiten,
- bereits bestätigte Ergebnisse an **allen fünf Klemmgrenzen** dürfen bei einem Replay nicht noch einmal auf den Charakter angewendet werden: Energie 0, Energie 100, Stress 0, Stress 100 und Ruf 0,
- zusätzlich werden jetzt **alle 14 realen Street-Begegnungen mit tatsächlichem Effekt** direkt aus dem produktiven Katalog an einer passenden Energie-/Stress-Grenze ausgeführt und danach identisch wiederholt.

## Was bedeutet das im Spiel?

Wenn eine Begegnung theoretisch `+10 Energie` gibt, du aber schon 99 Energie hast, werden tatsächlich nur `+1` angewendet. Dasselbe gilt umgekehrt bei negativen Effekten. Beim Ruf gilt entsprechend: Hast du 2 Ruf und eine Begegnung würde `-10` geben, werden tatsächlich nur `-2` angewendet und der neue Ruf ist 0.

Wird genau dieselbe bestätigte Begegnung später wegen Recovery oder Wiederholung erneut gelesen, bleibt der bereits bestätigte Grenzzustand unverändert. Das gilt regressionsgesichert für **Energie-Minimum, Energie-Maximum, Stress-Minimum, Stress-Maximum und Ruf-Floor**. Es entsteht kein zweiter Ressourcen- oder Rufeffekt, kein zweites Journal-Ergebnis und kein zusätzlicher Zustandswechsel. Der Replay liefert nur das bereits bestätigte Ergebnis zurück.

Die neue Katalogprüfung geht einen Schritt weiter: Sie verwendet nicht nur künstliche Testbegegnungen, sondern jede aktuell katalogisierte Begegnung mit realem Effekt. Damit wird gleichzeitig geprüft, dass die echten Katalogdaten weiterhin zur bestehenden Klemm- und Replaylogik passen.

## Was wurde bewusst nicht geändert?

- keine Begegnungswahrscheinlichkeiten,
- keine Energie-/Stress-/Rufwerte im Katalog,
- keine neue Street-Engine,
- keine neue Speicherlogik,
- keine Balanceänderung,
- keine zusätzliche Replay-Architektur.

Der Audit ist reine Qualitätssicherung: vorhandenes Verhalten wird an kanonischen Klemmgrenzen und mit den realen Street-Effektwerten regressionsgesichert.

## Spätere sinnvolle Erweiterungen

- **Ansatz-Katalog-Matrix:** Ein späterer test-only Audit kann die reale Katalogauswahl zusätzlich über alle vier Ansätze `balanced`, `recovery`, `network` und `scout` prüfen. Nutzen: schützt nicht nur Effekt und Replay, sondern auch die Zuordnung der vorhandenen Ansatzgewichte zur kanonischen Begegnungsauswahl.
- **Größenabhängige Matrix:** Falls der Street-Katalog deutlich wächst, kann dieselbe Prüfung kompakt als generierte Matrix nach Begegnung, Grenzrichtung und Replaystatus ausgewertet werden, ohne Runtime- oder Gameplaylogik zu verändern.
