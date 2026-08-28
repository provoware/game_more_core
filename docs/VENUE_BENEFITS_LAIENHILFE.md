# Venue Benefits – einfache Erklärung

Ein eigener Ort darf später einen echten Nutzen haben. Wichtig ist aber: Das Spiel darf keinen Bonus nur deshalb anzeigen, weil die Oberfläche ihn ausdenkt.

Aktuell sind zwei Dinge sicher bestätigt: **Du besitzt den Ort** und **deine Ausbauten verändern bereits fünf Ortswerte**. Diese Werte dürfen deshalb in einem Betriebsprofil verständlich angezeigt werden.

Das Betriebsprofil zeigt bei eigenen Orten jetzt alle fünf Werte mit ausgeschriebenen deutschen Bezeichnungen: **Prestige, Publikumskraft, Risiko, Underground-Faktor und Nutzen**. Es berechnet nichts neu und verändert nichts am Spielstand.

Die Eigentumsgrenze bleibt hart: Bei **nicht besessenen Orten** werden diese fünf Werte nicht als eigenes Betriebsprofil an die Property-Anzeige ausgegeben. Die vorhandenen Basiswerte bleiben intern für Karte und Bezirksdarstellung erhalten; daraus entsteht aber kein Besitz- oder Bonusversprechen.

Zusätzlich ist diese Grenze jetzt direkt abgesichert: Die Browseranzeige darf fehlende Besitzwerte nicht aus der internen Ortswert-Karte zurückholen. Für die sichtbare Zeile zählt ausschließlich `entries[*].effective_values` – fehlt dieser Besitzwert, bleibt das Betriebsprofil leer.

Der echte Chromium-Nachweis startet mit einem isolierten Spielstand, kauft über den normalen `property.purchase`-Pfad genau einen Ort und rendert danach den normalen A4-Server bei **760×680**, **Großer Schrift** und **Hohem Kontrast**. Der Test verlangt genau ein sichtbares Fünf-Werte-Profil beim eigenen Ort, kein solches Profil bei fremden Orten und keine horizontale Überbreite.

Neu prüft derselbe Browser-Nachweis nicht mehr nur die fünf Bezeichnungen: **Hinter jeder Bezeichnung muss tatsächlich ein sichtbarer numerischer Wert stehen.** Damit kann eine leere oder nur beschriftete Profilzeile nicht versehentlich als vollständig funktionierend durch die Release-Abnahme rutschen.

## Mechanik-Audit: Publikumskraft

Als erster einzelner Kandidat wurde **Publikumskraft (`audience_pull`)** gegen die bestehende Event-Abrechnung geprüft. Das Ergebnis ist aktuell **NO-GO für einen mechanischen Bonus**.

Der Grund ist einfach: Die Event-Abrechnung kennt heute Event, Geld und Charakter, aber keinen autoritativen Property-/Upgrade-State. Sie besitzt auch kein Receipt-Feld, das später eindeutig beweisen könnte, welcher Publikumskraft-Wert welchen Bonus erzeugt hat. Eine Prozentzahl einfach in den Gewinn einzurechnen wäre deshalb eine neue versteckte Regel und beim Replay fachlich nicht sauber erklärbar.

Auch Scene Jobs sind kein zulässiger Umweg: Ihr Vertrag verbietet fremd eingespeiste Payout- und Effektmodifikatoren.

Das bedeutet nicht, dass Publikumskraft dauerhaft wirkungslos bleiben muss. Vor einem späteren GO braucht genau ein Zielpfad eine eindeutige Event→Location-Zuordnung, eine begrenzte Formel, Journal-/Receipt-Evidence und denselben Effekt nach Reload/Replay.

### Schutz vor veraltetem Audit

Der neue Audit-Schutz merkt sich nicht nur „Property fehlt“, sondern die komplette heute gültige Abrechnungsfläche: Welche Zustände hineingehen dürfen, welche Effekte verarbeitet werden, wohin sie angewendet werden und welche Receipt-Regeln existieren.

Wenn sich dieser Vertrag später ändert, schlägt die Regression absichtlich an. Dann muss die Entscheidung neu geprüft werden, statt dass ein altes NO-GO oder ein neuer Bonus unbemerkt neben der tatsächlichen Spielregel weiterlebt.

Noch nicht erlaubt sind daher automatische Vorteile wie „mehr Events“, „billigerer Betrieb“, „mehr Kapazität“ oder „laufender Gewinn“. Für solche Wirkungen fehlt weiterhin eine eigene Spielregel, die Speichern, Wiederholen und Fehlerfälle eindeutig regelt.

## Merksatz

**Anzeigen, was bei deinem Ort bestätigt ist: ja. Einen Bonus erfinden, bevor Server, Journal und Replay dieselbe Ursache beweisen können: nein.**

Der nächste sinnvolle Gameplay-Schritt ist nach diesem Audit nicht eine allgemeine Bonusengine, sondern die Entscheidung, ob `audience_pull` durch eine kleine Erweiterung des kanonischen Settlement-Vertrags sauber autorisiert werden kann oder ob ein anderer einzelner Venue-Wert den besseren bestehenden Zielpfad besitzt.
