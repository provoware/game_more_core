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

Die Werte sind **Erwartungswerte**. Eine einzelne Begegnung kann anders ausfallen. Über sehr viele gleichartig gewichtete Auswahlen beschreibt der Wert aber die mathematische Richtung des Ansatzes.

## Was hat der Audit gefunden?

- Alle vier Ansätze haben im Mittel einen positiven Energie- und Rufeffekt sowie eine Stresssenkung.
- **Erholung** besitzt den höchsten durchschnittlichen Energiegewinn.
- **Netzwerk** besitzt die stärkste durchschnittliche Stresssenkung und den höchsten Rufgewinn.
- **Ausgeglichen dominiert Erkundung derzeit mathematisch in allen drei geprüften Erwartungswerten:** mehr Energie, stärkere Stresssenkung und etwas mehr Ruf.
- Zwischen den übrigen Ansatzpaaren besteht keine vollständige Dominanz.
- Die Rechnung nutzt ausschließlich den bestehenden `STREET_ENCOUNTER_MANIFEST`-Katalog. Es gibt keine Telemetrie, keine Systemzeit und keine zweite Zufalls- oder Effektlogik.

Die Dominanz ist ein **Balancebefund**, kein technischer Defekt. Dieser QA-Slice dokumentiert und regressionssichert ihn, verändert aber absichtlich noch keine Spielwerte. Dadurch kann eine spätere Balanceentscheidung gezielt und mit eigener Abnahme erfolgen.

## Was wurde bewusst nicht verändert?

Keine Begegnung, kein Gewicht, kein Effekt, kein Runtime-Service, kein Save, kein Journal und keine Benutzeroberfläche wurden verändert. Der Audit ist ein reines Sicherheitsnetz gegen unbeabsichtigte Balanceverschiebungen.

## Sinnvolle spätere Erweiterung

Als nächster Gameplay-Slice kann gezielt geprüft werden, ob **Erkundung** eine eigene Stärke bekommen soll, ohne neue Engine zu bauen. Zusätzlich könnte ein **Grenzzustands-Audit** später prüfen, wie Street-Effekte nahe Energie-/Stress-Grenzen wirken. Dafür muss zuerst der tatsächliche Clamping-/Ressourcenvertrag gezielt gelesen werden; dieser Slice erfindet keine neue Regel.
