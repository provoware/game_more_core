# Avatar-Kurzmarke: Abschneidung im echten Browser prüfen

## Worum geht es?

Die Crew-Kurzmarke ist an mehreren Stellen sehr kompakt: im HUD, auf eigenen Kartenorten und im eigenen Ranking-Eintrag. Eine ausreichend große Schrift allein garantiert noch nicht, dass der Text vollständig sichtbar bleibt.

Der bestehende Avatar-Context-Browsertest prüft deshalb zusätzlich die tatsächlich gerenderte Box im Browser. Er vergleicht `scrollWidth` mit `clientWidth` sowie `scrollHeight` mit `clientHeight`. Ist der Inhalt größer als seine sichtbare Box, schlägt der Test mit dem betroffenen Kontext und den Messwerten fehl.

## Was wird nicht verändert?

- keine zweite Avatar- oder Browserarchitektur
- keine neue Datenquelle
- keine Gameplay-, Save-, Journal-, Map- oder Rankinglogik
- kein CSS-Fix auf Verdacht

Ein CSS-Patch ist erst gerechtfertigt, wenn Chromium oder Firefox reales Clipping reproduzierbar melden.

## Firefox-Cold-Start im Gate

Beim ersten Remote-Lauf und beim unveränderten Wiederholungslauf zeigte der erste Firefox-Anti-Flake-Durchgang denselben Session-Start-Timeout, während der jeweils zweite Firefox-Durchgang den vollständigen Avatar-Context-Vertrag bestand. Deshalb erhält ausschließlich die bestehende WebDriver-Session-Erzeugung begrenzten Cold-Start-Spielraum: 55 statt 35 Sekunden.

Die eigentliche DOM-Grenze bleibt bei 40 Sekunden, zwei Anti-Flake-Läufe bleiben Pflicht und unterschiedliche Ergebnisse bleiben weiterhin `FLAKY` und blockieren die Release-Abnahme. Der Test wird damit nicht weicher; lediglich ein reproduzierbar zu knappes Startfenster wird an die reale Runner-Kaltstartzeit angepasst.

## Für Laien

Kurz gesagt: Der Test schaut nicht nur, ob die Buchstaben groß genug sind. Er prüft auch, ob die Buchstaben wirklich komplett in ihr Kästchen passen. Wenn etwas abgeschnitten wird, stoppt die Abnahme statt den Fehler zu übersehen. Firefox bekommt beim allerersten Start etwas mehr Zeit zum Hochfahren, danach gelten dieselben harten Prüfungen wie vorher.

## Spätere Verbesserungsidee

Falls künftig längere erlaubte Kurzmarken eingeführt werden, sollte derselbe Harness zusätzlich die längste katalogisierte bzw. erlaubte Kurzmarke als Grenzfall prüfen. Nutzen: neue Identitätsoptionen können erweitert werden, ohne kleine HUD-, Map- oder Rankingflächen unbemerkt zu überladen.
