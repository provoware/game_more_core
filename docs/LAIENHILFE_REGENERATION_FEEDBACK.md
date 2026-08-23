# Regenerationsfeedback – einfach erklärt

Nach einer bestätigten Regeneration zeigt BUNKERFREQUENZ direkt, was tatsächlich passiert ist.

Beispiel:

`Energie 40 → 60 · Stress 30 → 42`

Die Anzeige verwendet keine selbst ausgerechneten Spielwerte. Vor dem Klick liest die Oberfläche den bestätigten Character-Stand. Erst nachdem die Runtime die Regeneration bestätigt und den neuen Spielstand zurückgegeben hat, werden die neuen bestätigten Werte angezeigt.

Direkt dahinter erklärt die Oberfläche auch, ob die nächste Regeneration laut aktueller Runtime-Projection wieder möglich ist oder warum sie gesperrt ist.

## Wichtig

- Die Anzeige verändert keine Spielwerte.
- Die Regenerationsregel bleibt vollständig in der Runtime.
- Der Browser berechnet keine Energie- oder Stressdeltas.
- Der Browser berechnet keine Schwellenwerte.
- Ein abgewiesener oder unveränderter Vorgang erzeugt kein falsches Erfolgssignal.
- Es gibt weiterhin keine Echtzeitregeneration und keinen Rechnerzeit-Cooldown.

Die eigentliche Regenerationsmechanik ist weiterhin in [`LAIENHILFE_REGENERATION.md`](LAIENHILFE_REGENERATION.md) erklärt.