# Crew-Avatar auf der Berlin-Karte

## Was ist neu?

Deine bestätigte Crew-Marke erscheint jetzt bei eigenen Orten auf der Berlin-Karte und zusätzlich im Detailbereich eines ausgewählten eigenen Ortes.

## Was bedeutet die Marke?

Die Karte zeigt nur die bereits bestätigte Crew-Identität aus dem bestehenden Spielstand. Sie erzeugt keinen Besitz und verändert keine Werte.

- Nur Orte mit bestätigtem Eigentum bekommen die Crew-Marke.
- Fremde oder noch nicht gekaufte Orte bleiben unverändert.
- Das Detail zeigt dieselbe bestätigte Marke wie das Live-HUD.
- Änderungen im Profil erscheinen erst nach erfolgreichem Speichern.

## Was wurde bewusst nicht gebaut?

- keine zweite Avatar-Datenquelle,
- kein zusätzlicher `/api/state`-Abruf,
- keine neue Map-Projection,
- keine Kauf- oder Besitzlogik im Browser,
- keine externe Karten- oder Grafikbibliothek.

Die Karte bleibt vollständig read-only. Sie visualisiert nur bereits bestätigte Zustände.
