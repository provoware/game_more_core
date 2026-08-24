# Laienhilfe – Street-Effekt-Audit

## Was wurde geprüft?

BUNKERFREQUENZ besitzt vier Arten, wie eine Straßenrunde angegangen werden kann: **Ausgeglichen**, **Erholung**, **Netzwerk** und **Erkundung**. Diese Auswahl ändert nur die Chance, welche bereits vorhandene Straßenbegegnung erscheint. Die Begegnung selbst bestimmt weiterhin ihre Energie-, Stress- und Rufwirkung.

Der neue Audit verändert deshalb **keine Spielwerte**. Er rechnet lediglich nach, was die vorhandenen Gewichte und Effekte im Durchschnitt ergeben.

## Durchschnitt pro Straßenbegegnung

| Ansatz | Energie | Stress | Ruf |
|---|---:|---:|---:|
| Ausgeglichen | +1,00 | −0,49 | +0,35 |
| Erholung | +1,23 | −0,49 | +0,23 |
| Netzwerk | +0,53 | −0,59 | +0,65 |
| Erkundung | +0,91 | −0,14 | +0,33 |

Die Werte sind **Erwartungswerte**. Das bedeutet: Eine einzelne Begegnung kann natürlich anders ausfallen. Über sehr viele gleichartig gewichtete Auswahlen beschreibt der Wert aber die mathematische Richtung des Ansatzes.

## Was beweist der Test?

- Alle vier Ansätze haben im Mittel einen positiven Energie- und Rufeffekt sowie eine Stresssenkung.
- **Erholung** besitzt den höchsten durchschnittlichen Energiegewinn.
- **Netzwerk** besitzt die stärkste durchschnittliche Stresssenkung und den höchsten Rufgewinn.
- Kein Ansatz ist gleichzeitig bei Energie, Stress und Ruf mindestens so gut wie ein anderer und irgendwo besser. Es gibt also keinen global überlegenen Ansatz.
- Die Rechnung nutzt ausschließlich den bestehenden `STREET_ENCOUNTER_MANIFEST`-Katalog. Es gibt keine Telemetrie, keine Systemzeit und keine zweite Zufalls- oder Effektlogik.

## Was wurde bewusst nicht verändert?

Keine Begegnung, kein Gewicht, kein Effekt, kein Runtime-Service, kein Save, kein Journal und keine Benutzeroberfläche wurden verändert. Der Audit ist ein reines Sicherheitsnetz gegen spätere unbeabsichtigte Balanceverschiebungen.

## Sinnvolle spätere Erweiterung

Ein zusätzlicher **Grenzzustands-Audit** könnte später prüfen, wie dieselben kleinen Street-Effekte an Energie-/Stress-Grenzen wirken, wenn der Character bereits nahe 0 oder 100 liegt. Das sollte erst erfolgen, nachdem der tatsächliche Clamping-/Ressourcenvertrag gezielt gelesen wurde; dieser Slice erfindet dafür keine neue Regel.
