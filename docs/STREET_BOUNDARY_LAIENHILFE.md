# Street-Grenzwerte – Laienhilfe

## Was wurde geprüft?

Straßenbegegnungen dürfen Energie, Stress und Ruf verändern. Energie und Stress sind im Spiel auf **0 bis 100** begrenzt; neue Street-Ergebnisse dürfen Ruf nicht unter **0** drücken.

Der Grenzwert-Audit prüft deshalb ausdrücklich die kritischen Richtungen:

- positive Effekte dürfen Energie nicht über 100 und Stress nicht unter 0 drücken,
- negative Effekte dürfen Energie nicht unter 0 und Stress nicht über 100 drücken,
- negative Rufeffekte dürfen bei neuen Street-Ergebnissen den kanonischen Ruf-Floor 0 nicht unterschreiten,
- bereits bestätigte Ergebnisse an **allen fünf Klemmgrenzen** dürfen bei einem Replay nicht noch einmal auf den Charakter angewendet werden: Energie 0, Energie 100, Stress 0, Stress 100 und Ruf 0,
- alle realen Street-Begegnungen mit tatsächlichem Effekt werden direkt aus dem produktiven Katalog an einer passenden Energie-/Stress-Grenze ausgeführt und danach identisch wiederholt,
- zusätzlich wird die reale Katalogauswahl über **alle vier Spieleransätze `balanced`, `recovery`, `network` und `scout`** geprüft: Jede unter dem jeweiligen Ansatz tatsächlich auswählbare Begegnung wird deterministisch getroffen, mit ihrem unveränderten kanonischen Effekt angewendet und anschließend identisch replayt.

## Was bedeutet das im Spiel?

Wenn eine Begegnung theoretisch `+10 Energie` gibt, du aber schon 99 Energie hast, werden tatsächlich nur `+1` angewendet. Dasselbe gilt umgekehrt bei negativen Effekten. Beim Ruf gilt entsprechend: Hast du 2 Ruf und eine Begegnung würde `-10` geben, werden tatsächlich nur `-2` angewendet und der neue Ruf ist 0.

Wird genau dieselbe bestätigte Begegnung später wegen Recovery oder Wiederholung erneut gelesen, bleibt der bereits bestätigte Grenzzustand unverändert. Das gilt regressionsgesichert für **Energie-Minimum, Energie-Maximum, Stress-Minimum, Stress-Maximum und Ruf-Floor**. Es entsteht kein zweiter Ressourcen- oder Rufeffekt, kein zweites Journal-Ergebnis und kein zusätzlicher Zustandswechsel. Der Replay liefert nur das bereits bestätigte Ergebnis zurück.

Die Ansatz-Katalog-Matrix prüft außerdem die Spielerwahl selbst: Ein Ansatz darf nur verändern, **wie wahrscheinlich** eine Begegnung ausgewählt wird. Ist eine Begegnung ausgewählt, bleiben deren Energie-, Stress- und Rufeffekte dieselben. Ein Kataloggewicht von `0` bedeutet dabei bewusst „unter diesem Ansatz nicht auswählbar“ und wird nicht künstlich umgangen.

## Neuer Verteilungsnachweis

Mit `PYTHONPATH=src python3 tools/street_boundary_matrix_report.py` kann jetzt ein kompakter, reproduzierbarer Bericht erzeugt werden. Er zeigt für jede Kombination aus **Ansatz × Begegnung**:

- das deklarierte Gewicht,
- die tatsächlich durch den bestehenden Runtime-Selektor belegte Anzahl der 100 Buckets,
- den exakten Bucketbereich,
- die Polarität,
- die für den Effekt relevante Klemmgrenze.

Der entscheidende Schutz ist nicht nur eine Summenprüfung: Jeder Bucket von `0` bis `99` wird durch denselben `_select`-Pfad geführt, den die Street-Runtime verwendet. Für jeden Ansatz muss die beobachtete Bucket-Anzahl **exakt** dem Manifestgewicht entsprechen. Ein Gewicht `0` muss exakt `0` Runtime-Buckets besitzen. Dadurch fällt eine spätere Abweichung zwischen Manifest und Auswahlreihenfolge als Regression auf.

## Was wurde bewusst nicht geändert?

- keine Begegnungswahrscheinlichkeiten,
- keine Energie-/Stress-/Rufwerte im Katalog,
- keine neue Street-Engine,
- keine neue Speicherlogik,
- keine Balanceänderung,
- keine zusätzliche Replay-Architektur,
- keine künstliche Auswahl von Begegnungen mit Ansatzgewicht 0.

Der Audit ist reine Qualitätssicherung: vorhandenes Verhalten wird an kanonischen Klemmgrenzen, mit den realen Street-Effektwerten, über alle vier bestehenden Spieleransätze und jetzt zusätzlich gegen die vollständige 100-Bucket-Verteilung regressionsgesichert.

## Spätere sinnvolle Erweiterungen

- **Matrix-Diff bei Balanceänderungen:** Ein späterer QA-Slice kann zwei erzeugte Reports strukturiert vergleichen und nur tatsächlich veränderte Ansatz-/Encounter-Buckets hervorheben. Nutzen: Balanceänderungen werden im Review sofort sichtbar, ohne Telemetrie oder Gameplaylogik einzuführen.
- **Status-Sync nach Safe Merge:** Die kanonischen Statusdateien können nach bestätigten Safe-Merges automatisiert gegen den tatsächlich gemergten Iterationsstand geprüft werden. Nutzen: weniger Statusdrift bei schnellen, kleinen QA-Slices.
