# Property Visual Hierarchy – fokussierter Audit

## Ziel

Die vorhandene Property-Liste bei wachsender Ortszahl schneller erfassbar machen, ohne neue Property-Komponenten, Renderer oder Gameplaylogik einzuführen.

## Befund

`#property-panel` nutzt denselben generischen Halbbreiten-Panel- und Listenvertrag wie kleinere Informationsbereiche. Bei mehreren kaufbaren und ausgebauten Orten konkurrieren Ortsdaten, Standortwerte und Aktionsbuttons dadurch stärker um Breite als nötig.

## Kleinster Patch

- vorhandenes Property-Panel auf volle Arbeitsbreite setzen,
- vorhandene `equipment-row`-Einträge im Property-Kontext als zweispaltige Kartenfläche nutzen,
- Ortsdaten und Aktionszeile optisch trennen,
- unter 980 px auf eine Spalte zurückfallen,
- High Contrast und Reduced Motion explizit erhalten.

## Grenzen

Keine Änderung an `renderProperties`, `property.purchase`, `property.upgrade`, Preisen, Ausbauwerten, Persistenz, Projection oder Commands. Die bestehende Runtime bleibt alleinige Autorität.

## Abnahme

Die Presentation-Regression prüft, dass die bestehenden Property-Zielstellen weiterverwendet werden, die Änderung CSS-only bleibt und responsive/Accessibility-Fallbacks vorhanden sind.

## Spätere Verbesserungsidee

Erst nach echter Nutzung mit vielen gleichzeitig besessenen Orten sollte geprüft werden, ob ein **lokaler Anzeige-Filter „ALLE / EIGENTUM / KAUFBAR“** nötig ist. Er darf nur read-only filtern und keine zweite Property-Selektion oder Browserautorität erzeugen.
