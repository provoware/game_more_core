# Visual Hierarchy 3 – fokussierter Audit

## Ziel

Nicht das Control Deck neu gestalten, sondern die bereits starke Economy-Hierarchie als Vergleich nutzen und genau einen sichtbaren Hierarchiebruch beheben.

## Vergleich

Geprüft wurden die bestehenden Hauptflächen Event, Straße, Krise, Property, Map und Ranking auf drei Fragen:

1. Ist der aktuelle Zustand schnell erkennbar?
2. Ist die nächste wichtige Handlung klar von reiner Information getrennt?
3. Bleiben High Contrast, Reduced Motion und kleine Fenster ohne neue Komponenten erhalten?

## Befund

Straße besitzt bereits ausgewählte Karten plus eigene Aktionszeile. Krise trennt Folgenvorschau und Entscheidung. Map besitzt Summary, Filter, Karte und Detailfläche. Ranking trennt Saisonstatus und Rangliste. Property verwendet die bestehende Listenstruktur.

Der deutlichste verbleibende Bruch lag in der **Event-Steuerung**: Eventdaten, Überschrift der nächsten Aktion, Aktionsbuttons und Blocker lagen in einer generischen Panel-Hierarchie, obwohl dieser Bereich den zentralen Event-Fortschritt steuert.

## Kleinster Patch

- vorhandenes `#event-panel` auf volle Arbeitsbreite heben,
- vorhandene vier Event-Eckdaten als kompakte Statusreihe stärken,
- vorhandenes `#event-actions` als eigene Aktionsfläche hervorheben,
- vorhandenen `#blockers`-Hinweis direkt darunter klar absetzen,
- keine IDs, Commands, Renderer oder Runtime-Daten ändern.

Die Visual-Schicht liegt in `web/a4/visual_hierarchy_3.css` und wird über den bereits vorhandenen UI-Asset-Loader geladen. Es entsteht kein zweites Dashboard und kein zweites Designsystem.

## Sicherheitsgrenzen

- keine Gameplay-, Economy-, Save-, Journal- oder Projection-Änderung,
- keine neue Browserautorität,
- keine automatische Aktion,
- keine Animation erforderlich,
- expliziter High-Contrast- und Reduced-Motion-Fallback,
- mobile Statusreihe fällt zuerst auf zwei, dann auf eine Spalte zurück.

## Spätere Verbesserungsidee

Nach realer Nutzung sollte derselbe Audit höchstens **einen weiteren** Bereich auswählen. Besonders Property kann später geprüft werden, sobald mehrere Orte gleichzeitig besessen und ausgebaut sind. Erst dann lässt sich belastbar sagen, ob dessen Listenhierarchie unter echter Datenmenge zu flach wird.
