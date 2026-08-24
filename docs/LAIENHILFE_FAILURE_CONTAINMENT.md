# BUNKERFREQUENZ – automatische Robustheitsprüfung

## Kurz gesagt

Diese Prüfung soll typische technische Probleme absichtlich **vor deiner Nutzung** erzeugen. Das Spiel-ZIP wird dadurch nicht verändert. Stattdessen wird kontrolliert geprüft, ob der vorhandene Start- und Speicherweg bei schwierigen Bedingungen sauber funktioniert oder verständlich abbricht.

## Was automatisch ausprobiert wird

- Ordnernamen mit Leerzeichen und Umlauten,
- sehr lange Projektpfade,
- unterschiedliche Sprach-/Zeitzonen-Umgebungen,
- ein bereits belegter lokaler Port,
- ein Port, der erst direkt beim Serverstart verloren geht,
- wenig verfügbare Dateideskriptoren und begrenzter Speicher,
- ein simulierter voller Datenträger beim Anlegen des Spielstandordners,
- fremde laufende Prozesse, die BUNKERFREQUENZ niemals beenden darf,
- kontrollierte Abstürze zwischen Journal- und State-Schritten,
- beschädigte State-/Journalenden und Snapshot-Recovery,
- einen älteren kompatiblen Spielstandzustand.

## Warum die Prüfung zweimal läuft

Ein zufällig einmal erfolgreicher Test ist kein zuverlässiger Beweis. Deshalb wird die komplette Matrix zweimal in frischen Umgebungen ausgeführt.

- 🟢 Beide Läufe identisch erfolgreich: `PASS`
- 🟡 Ergebnisse unterscheiden sich: `FLAKY` und keine Freigabe
- 🔴 Derselbe Fehler tritt reproduzierbar auf: `FAIL` und keine Freigabe

Ein zweiter Lauf darf einen ersten Fehler also nicht einfach „weggrünen“.

## Was die Prüfung ausdrücklich nicht macht

Sie installiert nichts mit `sudo`, verändert keine Systempakete und baut keine absichtlichen Absturzschalter in dein Spiel ein. Auch Gameplay, Geld, Charakterwerte und Save-Regeln werden nicht verändert.

Browser und echter Desktop-Doppelklick werden hier ebenfalls nicht doppelt getestet. Dafür gibt es das getrennte `DESKTOP-BROWSER-E2E-PRO`-Subgate.

## Was das für die Freigabe bedeutet

Nach erfolgreicher Robustheitsprüfung besitzt der Release Autopilot einen belegten `failure_containment_pro=PASS`-Nachweis. Solange der echte Desktop-/Browser-Test noch fehlt, bleibt das Paket trotzdem in **QUARANTINE** und wird dir nicht als finales Benutzer-ZIP angeboten.

Dadurch sollst du technische Start-, Pfad-, Port-, Speicher- oder Recovery-Probleme nicht erst selbst finden müssen.
