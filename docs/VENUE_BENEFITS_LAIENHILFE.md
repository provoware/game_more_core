# Venue Benefits – einfache Erklärung

Ein eigener Ort darf später einen echten Nutzen haben. Wichtig ist aber: Das Spiel darf keinen Bonus nur deshalb anzeigen, weil die Oberfläche ihn ausdenkt.

Aktuell sind zwei Dinge sicher bestätigt: **Du besitzt den Ort** und **deine Ausbauten verändern bereits fünf Ortswerte**. Diese Werte dürfen deshalb in einem Betriebsprofil verständlich angezeigt werden.

Das Betriebsprofil zeigt bei eigenen Orten jetzt alle fünf Werte mit ausgeschriebenen deutschen Bezeichnungen: **Prestige, Publikumskraft, Risiko, Underground-Faktor und Nutzen**. Es berechnet nichts neu und verändert nichts am Spielstand.

Die Eigentumsgrenze bleibt hart: Bei **nicht besessenen Orten** werden diese fünf Werte nicht als eigenes Betriebsprofil an die Property-Anzeige ausgegeben. Die vorhandenen Basiswerte bleiben intern für Karte und Bezirksdarstellung erhalten; daraus entsteht aber kein Besitz- oder Bonusversprechen.

Zusätzlich ist diese Grenze jetzt direkt abgesichert: Die Browseranzeige darf fehlende Besitzwerte nicht aus der internen Ortswert-Karte zurückholen. Für die sichtbare Zeile zählt ausschließlich `entries[*].effective_values` – fehlt dieser Besitzwert, bleibt das Betriebsprofil leer.

Der echte Chromium-Nachweis startet mit einem isolierten Spielstand, kauft über den normalen `property.purchase`-Pfad genau einen Ort und rendert danach den normalen A4-Server bei **760×680**, **Großer Schrift** und **Hohem Kontrast**. Der Test verlangt genau ein sichtbares Fünf-Werte-Profil beim eigenen Ort, kein solches Profil bei fremden Orten und keine horizontale Überbreite.

Neu prüft derselbe Browser-Nachweis nicht mehr nur die fünf Bezeichnungen: **Hinter jeder Bezeichnung muss tatsächlich ein sichtbarer numerischer Wert stehen.** Damit kann eine leere oder nur beschriftete Profilzeile nicht versehentlich als vollständig funktionierend durch die Release-Abnahme rutschen.

Noch nicht erlaubt sind automatische Vorteile wie „mehr Events“, „billigerer Betrieb“, „mehr Kapazität“ oder „laufender Gewinn“. Für solche Wirkungen fehlt noch eine eigene Spielregel, die Speichern, Wiederholen und Fehlerfälle eindeutig regelt.

## Merksatz

**Anzeigen, was bei deinem Ort bestätigt ist: ja. Bei fremden Orten Besitznutzen vortäuschen, leere Werte als fertig ausgeben oder neue Wirkung erfinden: nein.**

Der nächste sinnvolle Gameplay-Schritt ist nach diesem Browser-Nachweis ein eigener fachlicher Audit für genau **einen** mechanischen Venue Benefit. Erst dann darf entschieden werden, ob einer der fünf Werte tatsächlich eine neue Spielwirkung bekommt.
