# Laienhilfe – Welcher BUNKERFREQUENZ-Stand ist eigentlich aktuell?

BUNKERFREQUENZ trennt bewusst **Produktrelease** und **Entwicklungsstand**. Deshalb können zwei unterschiedliche Versionsangaben gleichzeitig korrekt sein.

## Die drei wichtigsten Angaben

1. **Release-Baseline** – das zuletzt bewusst als Produktpaket freigegebene Release. Aktuell: `0.8.4-alpha.1`.
2. **Letzte validierte Feature-Stufe** – der neueste Entwicklungsstand, der die vorgesehenen GitHub-Prüfungen bestanden hat und sicher gemergt wurde. Aktuell: `0.8.7-C3`.
3. **Nächste Iteration** – der nächste geplante Entwicklungsschritt. Aktuell: `0.8.7-C4`.

## Was bedeutet C3 konkret?

C3 bedeutet: Die District-Welt-Ereignisse besitzen nicht nur eine deterministische Runtime, sondern sind jetzt kontrolliert in den normalen Application-Flow eingebunden. Genau ein autorisierter Trigger ist aktiv: `settlement.complete`. Erst nach einem bestätigten Settlement und einer bestätigten District-Zuordnung darf ein District-Ereignis ausgelöst werden.

Der Browser liefert dabei weder die Trigger-ID noch Effekte oder Zufallswerte. Retry und Reload dürfen deshalb weder neu würfeln noch dieselbe District-Folge doppelt anwenden.

Noch **nicht** enthalten ist eine eigene erzählerische Ereignis-Timeline im Control Deck. Genau das ist der nächste geplante Schritt C4.

## Wo nachsehen?

`PROJEKTSTATUS.json` ist die kanonische Maschinenquelle für diesen Stand. `TODO.md` erklärt die nächste Arbeit in lesbarer Form. `FEATURE_POOL.md` enthält spätere Ideen.

Wenn sich diese drei Dateien widersprechen, ist das ein Entwicklungsfehler und kein zweiter gültiger Projektstand. Der Runtime-Test `test_feature_status_consistency.py` prüft deshalb zusätzlich die wichtigsten C3-Aussagen.
