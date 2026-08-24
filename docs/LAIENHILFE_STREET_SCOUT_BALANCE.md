# Laienhilfe – Street-Scout-Balance

## Was wurde geändert?

Der Straßenansatz **Scout** war mathematisch schlechter als **Balanced**: Im Durchschnitt hatte Scout weniger Energiegewinn, weniger Stressabbau und weniger Rufgewinn. Damit gab es trotz eigener Beschreibung keinen echten spielerischen Grund, Scout zu wählen.

Scout bleibt jetzt innerhalb seines bisherigen Balancevertrags: gleicher Polaritätsmix, höchstens 20 Auswahlpunkte auf einer einzelnen Begegnung und unveränderte Encounter-Effekte. Innerhalb der negativen Scout-Begegnungen werden lediglich 5 Auswahlpunkte von `Baustellenumweg` zu `Verlorener Handschuh` verschoben. Der bereits vorhandene Discovery-Fokus `Abkürzung + Nützlicher Fund + Kabel-Tipp` bleibt mit **40 von 100 Auswahlpunkten** unverändert der stärkste aller Ansätze.

## Was bedeutet das im Spiel?

- **Recovery** bleibt der stärkste Ansatz für durchschnittlichen Energiegewinn.
- **Network** bleibt der stärkste Ansatz für Stressabbau und Ruf.
- **Balanced** bleibt der ruhige Allrounder.
- **Scout** vermeidet im eigenen Auswahlprofil Baustellenumwege und erreicht dadurch knapp den höchsten Energie-Erwartungswert gegenüber Balanced, bezahlt dies aber mit deutlich weniger Stressabbau und etwas weniger Ruf.

Der neue Scout-Erwartungswert lautet ungefähr:

- Energie: **+1,01**
- Stress: **−0,09**
- Ruf: **+0,33**

Zum Vergleich liegt Balanced bei **+1,00 / −0,49 / +0,35**. Scout besitzt damit eine kleine eigene Stärke, ohne Balanced, Recovery oder Network vollständig zu dominieren.

## Was wurde ausdrücklich nicht geändert?

Es gibt keine neue Zufallsengine, keine neue Encounter-Art, keine zusätzliche Persistenz und keine UI-Sonderlogik. Die Manifestversion bleibt `0.8.8-street-pack`, der Scout-Polaritätsmix bleibt `15 neutral / 60 positiv / 25 negativ`, und alle Begegnungseffekte selbst bleiben unverändert.
