# Laienhilfe – Recovery-Balance-Audit

## Worum geht es?

BUNKERFREQUENZ hat zwei bestätigte Regenerationsaktionen:

- `Koffein & kalte Luft`: +20 Energie, +12 Stress
- `Mate, Zucker & Vollgas`: +30 Energie, +20 Stress

Der Audit verändert diese Werte nicht. Er prüft nur automatisch, ob die beiden Möglichkeiten weiterhin sauber gegeneinander abgewogen sind und keine versteckte Gratisstrategie entsteht.

## Was wird geprüft?

### 1. Alle Energie-/Stress-Zustände

Energie und Stress liegen jeweils zwischen 0 und 100. Der Test prüft deshalb alle 10.201 Kombinationen von `0/0` bis `100/100` für beide Aktionen.

Eine Aktion darf nur verfügbar sein, wenn ihr kompletter Energiegewinn und ihr kompletter Stresspreis noch Platz haben.

Beispiel:

- Koffein bei Energie 80 / Stress 88 → danach exakt 100 / 100
- Koffein bei Energie 81 oder Stress 89 → gesperrt
- Vollgas bei Energie 70 / Stress 80 → danach exakt 100 / 100
- Vollgas bei Energie 71 oder Stress 81 → gesperrt

Damit kann der Stresspreis niemals durch eine 100er-Grenze abgeschnitten werden.

## 2. Keine Variante dominiert global

Wenn beide Aktionen verfügbar sind, gilt immer:

- `Vollgas` gibt mehr Energie,
- `Vollgas` kostet aber auch mehr Stress.

Dadurch ist keine Variante gleichzeitig bei Energie besser und beim Stress günstiger.

Die kleine Variante besitzt außerdem Zustände, in denen sie noch erlaubt ist, während `Vollgas` wegen der strengeren Grenzen bereits gesperrt ist.

## 3. Mehrfachfolgen

Der Audit verfolgt automatisch alle erreichbaren Folgen aus mehreren Regenerationsaktionen.

Dabei muss gelten:

- jeder Energiegewinn kostet immer positiven Stress,
- Energie und Stress steigen exakt um die katalogisierten Werte,
- kein Zwischenschritt überschreitet 100,
- keine Aktionsfolge besitzt eine bessere Energie-pro-Stress-Effizienz als die effizienteste einzelne Aktion.

Damit kann eine Folge aus mehreren Aktionen nicht plötzlich aus mathematischen Rundungs-, Clamp- oder Schwellenfehlern eine Gratisstrategie erzeugen.

## Was der Audit bewusst nicht macht

- keine Telemetrie
- keine Live-Spielerdaten
- keine neue Mechanik
- keine Änderung an Energie-/Stresswerten
- kein Cooldown
- keine Rechnerzeit
- keine Browser-Balance
- kein Save- oder Journal-Write

Der Test ist ausschließlich ein Schutznetz für den bestehenden Balancevertrag.

## Warum ist das hilfreich?

Wenn später jemand Recovery-Werte oder Schwellen ändert, wird automatisch geprüft, ob dadurch beispielsweise Kosten abgeschnitten werden, eine Option die andere vollständig verdrängt oder eine Mehrfachfolge unerwartet effizient wird.

So bleibt die Balance nachvollziehbar, ohne Spieler zu überwachen oder die Mechanik automatisch umzubauen.
