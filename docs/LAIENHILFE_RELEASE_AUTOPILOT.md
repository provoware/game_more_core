# BUNKERFREQUENZ – automatische Release-Freigabe

## Kurz gesagt

Ein neues Spiel-ZIP wird künftig nicht mehr allein deshalb ausgegeben, weil der Code gebaut werden konnte. Vor einer Freigabe prüft ein automatischer Release-Autopilot das fertige Paket selbst.

Das Ziel ist: **Du sollst technische Start-, Paket- und Integritätsfehler nicht erst selbst finden müssen.**

## Die vier möglichen Ergebnisse

### 🟢 RELEASE_READY

Alle vorgeschriebenen Prüfungen sind bestanden. Genau das bereits getestete ZIP wird freigegeben. Es wird danach nicht noch einmal neu gebaut.

### 🟡 QUARANTINE

Das Paket konnte technisch gebaut werden, aber mindestens ein verpflichtender Nachweis fehlt noch oder ist nicht eindeutig. Deshalb wird **bewusst kein Benutzer-ZIP** angeboten.

Das ist kein kaputter Build, sondern eine Sicherheitsentscheidung.

### 🔴 RELEASE_BLOCKED

Eine verpflichtende Prüfung ist fehlgeschlagen. Das Paket wird nicht ausgeliefert.

### ⚫ RELEASE_INVALID

Policy, Dateimanifest oder Prüfnachweise widersprechen sich. Das Paket gilt als nicht vertrauenswürdig und wird ebenfalls nicht ausgeliefert.

## Was automatisch geprüft wird

Der Autopilot baut den Kandidaten zweimal und verlangt identische Bytes. Danach kontrolliert er jede katalogisierte Paketdatei auf SHA-256, Dateigröße und Dateirechte. Anschließend wird das ZIP in einen frischen Ordner entpackt und über den echten Startweg bis `100 % BEREIT` gestartet.

Erst danach werden die weiteren verpflichtenden Freigaben berücksichtigt.

## Warum aktuell eventuell kein ZIP erscheint

Der neue PRO-Vertrag verlangt zusätzlich zwei noch folgende Qualitätsstufen:

- echten Linux-Desktop-/Browser-E2E-Test,
- erweiterte Failure-Containment-/Stressprüfung.

Solange diese Nachweise noch fehlen, lautet der korrekte Zustand **QUARANTINE**. Der Workflow darf dann zwar grün sein, aber nur weil er korrekt bewiesen hat, dass kein ungeprüftes ZIP ausgeliefert wurde.

## Was sich für dich ändert

Du musst nicht mehr prüfen, ob ein ZIP technisch überhaupt startbar, vollständig oder identisch mit dem getesteten Build ist. Diese Aufgaben sollen vor der Freigabe automatisch erledigt werden.

Deine freiwillige Prüfung kann sich damit auf Dinge konzentrieren, die Maschinen nicht zuverlässig entscheiden können: Spielgefühl, Gestaltung, Verständlichkeit und persönliche Vorlieben.

## Wichtige Sicherheitsregel

Der Release-Autopilot installiert keine Systempakete, verwendet kein `sudo`, löscht keine Nutzerdaten und verändert keinen Spielstand. Er entscheidet ausschließlich über Build, Prüfung, Quarantäne und Freigabe des Release-Artefakts.
