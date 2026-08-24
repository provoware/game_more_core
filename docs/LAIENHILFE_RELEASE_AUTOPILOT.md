# BUNKERFREQUENZ – automatische Release-Freigabe

## Kurz gesagt

Ein neues Spiel-ZIP wird künftig nicht mehr allein deshalb ausgegeben, weil der Code gebaut werden konnte. Vor einer Freigabe prüft ein automatischer Release-Autopilot das fertige Paket selbst.

Das Ziel ist: **Du sollst technische Start-, Paket- und Integritätsfehler nicht erst selbst finden müssen.**

## Die vier möglichen Ergebnisse

### 🟢 RELEASE_READY

Alle vorgeschriebenen Prüfungen sind bestanden. Genau das bereits getestete ZIP wird freigegeben. Es wird danach nicht noch einmal neu gebaut.

### 🟡 QUARANTINE

Das Paket konnte technisch gebaut und im Clean-Room gestartet werden, aber mindestens ein verpflichtender Nachweis fehlt noch oder ist nicht eindeutig. Deshalb wird **bewusst kein Benutzer-ZIP** angeboten.

Das ist kein kaputter Build, sondern eine Sicherheitsentscheidung.

### 🔴 RELEASE_BLOCKED

Eine verpflichtende Prüfung ist fehlgeschlagen. Das Paket wird nicht ausgeliefert.

### ⚫ RELEASE_INVALID

Source-Stand, Policy, Dateimanifest oder Prüfnachweise widersprechen sich. Das Paket gilt als nicht vertrauenswürdig und wird ebenfalls nicht ausgeliefert.

## Was automatisch geprüft wird

Der Autopilot verlangt zuerst einen sauberen, eindeutig einem Commit zuordenbaren Projektstand. Danach baut er den Kandidaten zweimal in getrennten temporären Bereichen und verlangt identische Bytes.

Anschließend kontrolliert er jede katalogisierte Paketdatei auf SHA-256, Dateigröße und Dateirechte. Das ZIP wird in einen frischen Clean-Room entpackt, ohne Hilfe aus dem Entwickler-Projektpfad, und über den echten Startweg bis `100 % BEREIT` gestartet.

Spätere Desktop-/Robustheitstests dürfen ein `PASS` nur für exakt denselben Commit und Source Tree liefern. Ein alter grüner Test kann deshalb keinen neuen Build freigeben.

## Warum aktuell eventuell kein ZIP erscheint

Der PRO-Vertrag verlangt zusätzlich zwei noch folgende Qualitätsstufen:

- echten Linux-Desktop-/Browser-E2E-Test,
- erweiterte Failure-Containment-/Stressprüfung.

Solange diese Nachweise noch fehlen, lautet der korrekte Zustand **QUARANTINE**. Der Workflow darf dabei grün sein, weil er korrekt bewiesen hat, dass **kein ungeprüftes ZIP** ausgeliefert wurde.

## Was sich für dich ändert

Du musst nicht mehr prüfen, ob ein ZIP technisch überhaupt startbar, vollständig oder identisch mit dem getesteten Build ist. Ein technisch nicht vollständig belegtes Paket wird dir gar nicht erst als Release angeboten.

Deine freiwillige Prüfung kann sich damit auf Dinge konzentrieren, die Maschinen nicht zuverlässig entscheiden können: Spielgefühl, Gestaltung, Verständlichkeit und persönliche Vorlieben.

## Wichtige Sicherheitsregel

Der Release-Autopilot installiert keine Systempakete, verwendet kein `sudo`, löscht keine Nutzerdaten und verändert keinen Spielstand. Er entscheidet ausschließlich über Build, Prüfung, Quarantäne und Freigabe des Release-Artefakts.
