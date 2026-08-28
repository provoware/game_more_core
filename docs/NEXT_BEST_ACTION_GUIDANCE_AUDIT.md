# Next-Best-Action-Guidance Audit

## Ziel

Die vorhandene „Nächster Schritt“-Hilfe so erweitern, dass sie im Control Deck verständlicher führt, ohne eine zweite Recommendation- oder Gameplay-Engine im Browser zu erzeugen.

## Befund

Die vorhandene Presentation besitzt bereits einen sicheren Runtime-Anker: freigegebene Event-Aktionen werden aus dem gerenderten Runtime-Zustand erkannt und hervorgehoben. Zusätzlich existieren bereits zwei weitere eindeutige, nicht interpretative Signale:

1. Der sichtbare Erststart mit dem vorhandenen Button `#new-game`.
2. Der vorhandene Klartext-Blocker `#blockers`, dessen Inhalt aus den Runtime-Event-Gates stammt.

Dagegen wären Empfehlungen wie „erst erholen“, „jetzt handeln“ oder „Geld sparen“ derzeit Browser-Heuristiken. Energie, Bargeld oder Marktpreise allein beweisen keine beste nächste Handlung.

## Entscheidung

Der kleinste sichere Ausbau nutzt ausschließlich:

- sichtbaren Erststart → „Neues Spiel anlegen“;
- bereits freigegebene Event-Aktion → vorhandenen Button hervorheben;
- bereits bestätigten Event-Blocker → Blockiergrund oben kompakt erklären;
- keinen dieser Fälle → keine erfundene Strategie, sondern neutral melden, dass keine normale Event-Aktion freigegeben ist.

## Architekturgrenze

Die Guidance bleibt reine Presentation:

- kein `fetch` und kein eigener Command;
- kein eigener persistenter Zustand;
- keine Auswertung von Energie, Bargeld oder Marktpreisen zu einer Strategie;
- keine automatische Aktion;
- keine neue Empfehlungstabelle parallel zur Runtime.

## Regression

`tests/presentation/test_a4_control_deck_focus.py` sichert Erststart, freigegebene Runtime-Aktion, Blocker-Klartext, fehlende Browser-Heuristiken und den vorhandenen MutationObserver-Schutz ab.

## Spätere Verbesserungsidee

Soll später eine echte situationsabhängige Empfehlung wie „erst erholen“ entstehen, braucht die Runtime zuerst einen kleinen read-only Empfehlungshinweis mit klarer Autorität und Gründen. Erst dann darf die Presentation diesen Hinweis anzeigen. Das verhindert, dass dieselben Regeln gleichzeitig in Runtime und Browser gepflegt werden müssen.
