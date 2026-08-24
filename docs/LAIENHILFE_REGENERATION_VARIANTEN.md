# Laienhilfe – Zwei Regenerationsentscheidungen

BUNKERFREQUENZ bietet jetzt zwei aktive Regenerationswege. Beide sind bestätigte Character-Aktionen und beide haben einen Preis: **mehr Energie bedeutet mehr Stress**.

## 1. Koffein & kalte Luft

- `+20 Energie`
- `+12 Stress`
- nur möglich bis einschließlich `80 Energie`
- nur möglich bis einschließlich `88 Stress`

Das ist der **sparsamere Reset**. Du bekommst weniger Energie auf einmal, bezahlst dafür aber auch weniger Stress.

## 2. Mate, Zucker & Vollgas

- `+30 Energie`
- `+20 Stress`
- nur möglich bis einschließlich `70 Energie`
- nur möglich bis einschließlich `80 Stress`

Das ist der **größere Sofortschub**. Er ist bewusst nicht effizienter: Für 50 % mehr Energie bezahlst du ungefähr 66,7 % mehr Stress.

## Beispiel

Bei `70 Energie / 40 Stress` ergibt sich:

- Koffein & kalte Luft → `90 Energie / 52 Stress`
- Mate, Zucker & Vollgas → `100 Energie / 60 Stress`

Du entscheidest also zwischen weniger Belastung und mehr sofortiger Reserve.

## Warum kann eine Aktion gesperrt sein?

Die Runtime prüft vor jeder Regeneration, ob der komplette Energiegewinn und der komplette Stresspreis noch Platz haben. Es wird nichts heimlich auf 100 abgeschnitten, damit der Preis nicht billiger wird.

Beispiel: Bei `60 Energie / 81 Stress` ist der große Vollgas-Schub gesperrt, weil `+20 Stress` nicht mehr vollständig möglich wäre. Die kleinere `+12`-Variante kann in diesem Zustand noch erlaubt sein.

## Was passiert nicht?

- keine automatische Regeneration mit der Rechneruhr
- kein Echtzeit-Cooldown
- kein Zufall
- keine zusätzlichen XP oder Traits
- keine zweite Ressourcen- oder Recovery-Engine
- der Browser legt weder Energie-/Stresswerte noch Grenzwerte fest

Der Browser wählt nur die gewünschte Regenerationsaktion. Die bestätigten Werte, die Verfügbarkeit, das Journal und Recovery bleiben Aufgabe der Runtime.

Technischer Balancevertrag: [`RECOVERY_VARIANTS_BALANCE_CONTRACT.md`](RECOVERY_VARIANTS_BALANCE_CONTRACT.md)
