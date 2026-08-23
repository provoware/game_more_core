# Laienhilfe – Welcher BUNKERFREQUENZ-Stand ist eigentlich aktuell?

BUNKERFREQUENZ trennt bewusst **Produktrelease** und **Entwicklungsstand**. Deshalb können zwei unterschiedliche Versionsangaben gleichzeitig korrekt sein.

## Die drei wichtigsten Angaben

1. **Release-Baseline** – das zuletzt bewusst als Produktpaket freigegebene Release. Aktuell: `0.8.4-alpha.1`.
2. **Letzte validierte Feature-Stufe** – der neueste Entwicklungsstand, der die vorgesehenen GitHub-Prüfungen bestanden hat und sicher gemergt wurde. Aktuell: `0.8.7-C2`.
3. **Nächste Iteration** – der nächste geplante Entwicklungsschritt. Aktuell: `0.8.7-C3`.

## Was bedeutet C2 konkret?

C2 bedeutet: Die District-Welt-Ereignisse besitzen bereits eine deterministische Runtime. Derselbe bestätigte Kontext würfelt beim Reload nicht neu, Effekte laufen über den vorhandenen DistrictService und der Ereigniskatalog wird beim Start auf typische Fehler geprüft.

Noch **nicht** enthalten ist die automatische Auslösung aus dem normalen A4-Spielablauf. Genau das ist der nächste Schritt C3.

## Wo nachsehen?

`PROJEKTSTATUS.json` ist die kanonische Maschinenquelle für diesen Stand. `TODO.md` erklärt die nächste Arbeit in lesbarer Form. `FEATURE_POOL.md` enthält spätere Ideen.

Wenn sich diese drei Dateien widersprechen, ist das ein Entwicklungsfehler und kein zweiter gültiger Projektstand. Der Runtime-Test `test_feature_status_consistency.py` prüft deshalb zusätzlich die wichtigsten C2-Aussagen.
