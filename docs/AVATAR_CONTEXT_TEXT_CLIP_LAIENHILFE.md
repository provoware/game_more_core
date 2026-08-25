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

## Für Laien

Kurz gesagt: Der Test schaut nicht nur, ob die Buchstaben groß genug sind. Er prüft auch, ob die Buchstaben wirklich komplett in ihr Kästchen passen. Wenn etwas abgeschnitten wird, stoppt die Abnahme statt den Fehler zu übersehen.

## Spätere Verbesserungsidee

Falls künftig längere erlaubte Kurzmarken eingeführt werden, sollte derselbe Harness zusätzlich die längste katalogisierte bzw. erlaubte Kurzmarke als Grenzfall prüfen. Nutzen: neue Identitätsoptionen können erweitert werden, ohne kleine HUD-, Map- oder Rankingflächen unbemerkt zu überladen.
