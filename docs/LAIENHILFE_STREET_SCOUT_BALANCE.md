# Laienhilfe – Street-Scout-Balance

## Was wurde geändert?

Der Straßenansatz **Scout** war mathematisch schlechter als **Balanced**: Im Durchschnitt hatte Scout weniger Energiegewinn, weniger Stressabbau und weniger Rufgewinn. Damit gab es trotz eigener Beschreibung keinen echten spielerischen Grund, Scout zu wählen.

Jetzt bleibt Scout bewusst ein Erkundungsansatz. Seine Wahrscheinlichkeit für die drei entdeckungsnahen Begegnungen `Abkürzung`, `Nützlicher Fund` und `Kabel-Tipp` steigt zusammen auf **45 von 100 Auswahlpunkten**. Dafür bleibt Scout beim Stressabbau und Ruf schwächer als andere Ansätze.

## Was bedeutet das im Spiel?

- **Recovery** bleibt der stärkste Ansatz für durchschnittlichen Energiegewinn.
- **Network** bleibt der stärkste Ansatz für Stressabbau und Ruf.
- **Balanced** bleibt der ruhige Allrounder.
- **Scout** setzt stärker auf Abkürzungen und Funde und ist nicht mehr vollständig von Balanced dominiert.

Der neue Scout-Erwartungswert lautet ungefähr:

- Energie: **+1,16**
- Stress: **−0,29**
- Ruf: **+0,33**

Zum Vergleich liegt Balanced bei **+1,00 / −0,49 / +0,35**. Scout gewinnt damit im Mittel mehr Energie als Balanced, bezahlt diesen Vorteil aber mit weniger Stressabbau und etwas weniger Ruf.

## Was wurde ausdrücklich nicht geändert?

Es gibt keine neue Zufallsengine, keine neue Encounter-Art, keine zusätzliche Persistenz und keine UI-Sonderlogik. Nur die bereits vorhandenen Scout-Auswahlgewichte wurden im bestehenden Street-Manifest verschoben. Alle Begegnungseffekte selbst bleiben unverändert.
